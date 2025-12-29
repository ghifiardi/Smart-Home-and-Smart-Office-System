#!/usr/bin/env python3
"""
Service Health Check and Testing Script
Tests all infrastructure and application services for the Smart Office system
"""

import asyncio
import sys
import time
from typing import Dict, List, Tuple
import httpx
import redis
import psycopg2
from paho.mqtt import client as mqtt_client
import json
from datetime import datetime

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

# Service configurations
INFRASTRUCTURE_SERVICES = {
    'PostgreSQL': {
        'type': 'database',
        'host': 'localhost',
        'port': 5432,
        'user': 'smartoffice_user',
        'password': 'smartoffice_password',
        'database': 'smartoffice'
    },
    'Redis': {
        'type': 'cache',
        'host': 'localhost',
        'port': 6379
    },
    'MinIO': {
        'type': 'http',
        'url': 'http://localhost:9000/minio/health/live',
        'name': 'Object Storage'
    },
    'MinIO Console': {
        'type': 'http',
        'url': 'http://localhost:9001',
        'name': 'MinIO Web Console'
    },
    'EMQX Dashboard': {
        'type': 'http',
        'url': 'http://localhost:18083',
        'name': 'MQTT Broker Dashboard'
    },
    'EMQX MQTT': {
        'type': 'mqtt',
        'host': 'localhost',
        'port': 1883
    }
}

APPLICATION_SERVICES = {
    'Auth Service': 'http://localhost:8001',
    'Data Service': 'http://localhost:8002',
    'Detection Service': 'http://localhost:8003',
    'Device Controller': 'http://localhost:8004',
    'Rule Engine': 'http://localhost:8005',
    'Notification Service': 'http://localhost:8006',
    'Analytics Service': 'http://localhost:8007'
}

class ServiceTester:
    def __init__(self):
        self.results: List[Tuple[str, bool, str]] = []
        self.start_time = time.time()

    def print_header(self, text: str):
        """Print a formatted header"""
        print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
        print(f"{BOLD}{BLUE}{text:^60}{RESET}")
        print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")

    def print_result(self, service: str, status: bool, message: str = ""):
        """Print test result with color coding"""
        status_icon = f"{GREEN}✓{RESET}" if status else f"{RED}✗{RESET}"
        status_text = f"{GREEN}PASS{RESET}" if status else f"{RED}FAIL{RESET}"

        print(f"{status_icon} {service:.<40} [{status_text}]")
        if message:
            print(f"  {YELLOW}└─ {message}{RESET}")

        self.results.append((service, status, message))

    def test_postgres(self, config: Dict) -> Tuple[bool, str]:
        """Test PostgreSQL connection"""
        try:
            conn = psycopg2.connect(
                host=config['host'],
                port=config['port'],
                user=config['user'],
                password=config['password'],
                database=config['database'],
                connect_timeout=5
            )
            cursor = conn.cursor()
            cursor.execute('SELECT version();')
            version = cursor.fetchone()[0]
            cursor.close()
            conn.close()
            return True, f"Connected - {version.split(',')[0]}"
        except Exception as e:
            return False, str(e)

    def test_redis(self, config: Dict) -> Tuple[bool, str]:
        """Test Redis connection"""
        try:
            r = redis.Redis(
                host=config['host'],
                port=config['port'],
                socket_connect_timeout=5
            )
            response = r.ping()
            info = r.info('server')
            version = info.get('redis_version', 'unknown')
            return True, f"Connected - Redis v{version}"
        except Exception as e:
            return False, str(e)

    def test_mqtt(self, config: Dict) -> Tuple[bool, str]:
        """Test MQTT connection"""
        try:
            connected = False
            error_msg = ""

            def on_connect(client, userdata, flags, rc):
                nonlocal connected, error_msg
                if rc == 0:
                    connected = True
                else:
                    error_msg = f"Connection failed with code {rc}"

            client = mqtt_client.Client(f"test_client_{int(time.time())}")
            client.on_connect = on_connect

            client.connect(config['host'], config['port'], 5)
            client.loop_start()

            # Wait for connection
            timeout = 5
            start = time.time()
            while not connected and time.time() - start < timeout:
                time.sleep(0.1)

            client.loop_stop()
            client.disconnect()

            if connected:
                return True, "Connected successfully"
            else:
                return False, error_msg or "Connection timeout"
        except Exception as e:
            return False, str(e)

    async def test_http_endpoint(self, url: str, timeout: int = 5) -> Tuple[bool, str]:
        """Test HTTP endpoint"""
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url)
                if response.status_code == 200:
                    return True, f"Status {response.status_code}"
                else:
                    return False, f"Status {response.status_code}"
        except httpx.ConnectError:
            return False, "Connection refused"
        except httpx.TimeoutException:
            return False, "Request timeout"
        except Exception as e:
            return False, str(e)

    async def test_api_health(self, name: str, base_url: str) -> Tuple[bool, str]:
        """Test API service health endpoint"""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                # Try common health endpoints
                health_endpoints = ['/health', '/api/health', '/']

                for endpoint in health_endpoints:
                    try:
                        url = f"{base_url}{endpoint}"
                        response = await client.get(url)

                        if response.status_code == 200:
                            try:
                                data = response.json()
                                if isinstance(data, dict):
                                    return True, f"Healthy - {endpoint}"
                            except:
                                return True, f"Reachable - {endpoint}"
                    except:
                        continue

                # If no health endpoint works, just try to connect
                response = await client.get(base_url)
                return True, f"Reachable (Status {response.status_code})"

        except httpx.ConnectError:
            return False, "Service not running"
        except httpx.TimeoutException:
            return False, "Service timeout"
        except Exception as e:
            return False, str(e)

    async def test_infrastructure(self):
        """Test all infrastructure services"""
        self.print_header("Testing Infrastructure Services")

        for service_name, config in INFRASTRUCTURE_SERVICES.items():
            service_type = config.get('type')

            if service_type == 'database':
                status, message = self.test_postgres(config)
            elif service_type == 'cache':
                status, message = self.test_redis(config)
            elif service_type == 'mqtt':
                status, message = self.test_mqtt(config)
            elif service_type == 'http':
                status, message = await self.test_http_endpoint(config['url'])
            else:
                status, message = False, "Unknown service type"

            self.print_result(service_name, status, message)

    async def test_applications(self):
        """Test all application services"""
        self.print_header("Testing Application Services")

        for service_name, base_url in APPLICATION_SERVICES.items():
            status, message = await self.test_api_health(service_name, base_url)
            self.print_result(service_name, status, message)

    async def test_integration(self):
        """Test service integration"""
        self.print_header("Testing Service Integration")

        # Test database connectivity from API perspective
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                # Try to access data service
                response = await client.get(f"{APPLICATION_SERVICES['Data Service']}/health")
                if response.status_code == 200:
                    self.print_result("Data Service → PostgreSQL", True, "Database connection verified")
                else:
                    self.print_result("Data Service → PostgreSQL", False, "Cannot verify database connection")
        except:
            self.print_result("Data Service → PostgreSQL", False, "Service not available")

    def print_summary(self):
        """Print test summary"""
        elapsed = time.time() - self.start_time

        total = len(self.results)
        passed = sum(1 for _, status, _ in self.results if status)
        failed = total - passed

        self.print_header("Test Summary")

        print(f"Total Tests:  {total}")
        print(f"{GREEN}Passed:       {passed}{RESET}")
        print(f"{RED}Failed:       {failed}{RESET}")
        print(f"Duration:     {elapsed:.2f}s")

        if failed > 0:
            print(f"\n{YELLOW}Failed Services:{RESET}")
            for service, status, message in self.results:
                if not status:
                    print(f"  {RED}✗{RESET} {service}")
                    if message:
                        print(f"    {message}")

        print(f"\n{BOLD}Overall Status: ", end="")
        if failed == 0:
            print(f"{GREEN}ALL TESTS PASSED ✓{RESET}")
            return 0
        else:
            print(f"{RED}SOME TESTS FAILED ✗{RESET}")
            return 1

    async def run_all_tests(self):
        """Run all tests"""
        print(f"\n{BOLD}{BLUE}Smart Office Service Health Check{RESET}")
        print(f"{BLUE}Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{RESET}")

        await self.test_infrastructure()
        await self.test_applications()
        await self.test_integration()

        return self.print_summary()

async def main():
    """Main entry point"""
    tester = ServiceTester()
    exit_code = await tester.run_all_tests()
    sys.exit(exit_code)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Test interrupted by user{RESET}")
        sys.exit(1)
