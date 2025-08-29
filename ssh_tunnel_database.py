#!/usr/bin/env python3
"""
SSH Tunnel Database Connection Script
This script creates an SSH tunnel to access the remote database through the jump server.
"""
import os
import sys
import time
import subprocess
import psycopg2
from dotenv import load_dotenv
import threading

# Load environment variables
load_dotenv()

class SSHTunnel:
    def __init__(self):
        self.ssh_host = "88.223.94.231"
        self.ssh_user = "ubuntu"
        self.ssh_port = 22
        self.local_port = 5433  # Local port to forward to
        self.remote_host = "35.197.215.50"  # Database server
        self.remote_port = 5432
        self.tunnel_process = None
        
    def create_tunnel(self):
        """Create SSH tunnel"""
        try:
            print(f"🔗 Creating SSH tunnel...")
            print(f"   SSH Server: {self.ssh_user}@{self.ssh_host}:{self.ssh_port}")
            print(f"   Local Port: {self.local_port}")
            print(f"   Remote Database: {self.remote_host}:{self.remote_port}")
            
            # SSH tunnel command
            ssh_command = [
                "ssh",
                "-N",  # Don't execute remote command
                "-L", f"{self.local_port}:{self.remote_host}:{self.remote_port}",  # Local port forwarding
                f"{self.ssh_user}@{self.ssh_host}",
                "-o", "StrictHostKeyChecking=no",  # Don't prompt for host key verification
                "-o", "UserKnownHostsFile=/dev/null",  # Don't save host key
                "-o", "LogLevel=ERROR"  # Reduce SSH output
            ]
            
            print(f"🚀 Starting SSH tunnel...")
            print(f"Command: {' '.join(ssh_command)}")
            
            # Start SSH tunnel in background
            self.tunnel_process = subprocess.Popen(
                ssh_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait a moment for tunnel to establish
            time.sleep(3)
            
            # Check if tunnel is still running
            if self.tunnel_process.poll() is None:
                print("✅ SSH tunnel established successfully!")
                return True
            else:
                stdout, stderr = self.tunnel_process.communicate()
                print(f"❌ SSH tunnel failed to start:")
                print(f"   stdout: {stdout.decode()}")
                print(f"   stderr: {stderr.decode()}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to create SSH tunnel: {e}")
            return False
    
    def close_tunnel(self):
        """Close SSH tunnel"""
        if self.tunnel_process:
            print("🔒 Closing SSH tunnel...")
            self.tunnel_process.terminate()
            self.tunnel_process.wait()
            print("✅ SSH tunnel closed")

def test_database_connection(tunnel):
    """Test database connection through SSH tunnel"""
    try:
        print("\n🧪 Testing database connection through tunnel...")
        
        # Create connection string for tunneled connection
        tunneled_connection = f"postgresql://cat_manager:004IuYdPgdNtzhYpCFNc2ngzyO6soW@localhost:{tunnel.local_port}/aicategorymapping"
        
        print(f"🔗 Connecting to: localhost:{tunnel.local_port} (tunneled to {tunnel.remote_host}:{tunnel.remote_port})")
        
        # Test connection
        conn = psycopg2.connect(tunneled_connection)
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Connection successful!")
        print(f"📊 PostgreSQL version: {version[0]}")
        
        # Test database info
        cursor.execute("SELECT current_database(), current_user;")
        db_info = cursor.fetchone()
        print(f"🗄️  Database: {db_info[0]}")
        print(f"👤 User: {db_info[1]}")
        
        # List tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        
        if tables:
            print(f"📋 Tables found ({len(tables)}):")
            for table in tables:
                print(f"   - {table[0]}")
        else:
            print("📋 No tables found in public schema")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def update_env_for_tunnel(tunnel):
    """Update .env file to use tunneled connection"""
    try:
        print(f"\n📝 Updating .env file for SSH tunnel...")
        
        # Read current .env
        env_lines = []
        if os.path.exists('.env'):
            with open('.env', 'r') as f:
                env_lines = f.readlines()
        
        # Update connection settings
        new_env_lines = []
        updated_vars = set()
        
        for line in env_lines:
            if line.startswith('POSTGRES_HOST='):
                new_env_lines.append('POSTGRES_HOST=localhost\n')
                updated_vars.add('POSTGRES_HOST')
            elif line.startswith('POSTGRES_PORT='):
                new_env_lines.append(f'POSTGRES_PORT={tunnel.local_port}\n')
                updated_vars.add('POSTGRES_PORT')
            elif line.startswith('POSTGRES_CONNECTION_STRING='):
                new_connection = f"postgresql://cat_manager:004IuYdPgdNtzhYpCFNc2ngzyO6soW@localhost:{tunnel.local_port}/aicategorymapping"
                new_env_lines.append(f'POSTGRES_CONNECTION_STRING={new_connection}\n')
                updated_vars.add('POSTGRES_CONNECTION_STRING')
            else:
                new_env_lines.append(line)
        
        # Add missing variables
        if 'POSTGRES_HOST' not in updated_vars:
            new_env_lines.append('POSTGRES_HOST=localhost\n')
        if 'POSTGRES_PORT' not in updated_vars:
            new_env_lines.append(f'POSTGRES_PORT={tunnel.local_port}\n')
        if 'POSTGRES_CONNECTION_STRING' not in updated_vars:
            new_connection = f"postgresql://cat_manager:004IuYdPgdNtzhYpCFNc2ngzyO6soW@localhost:{tunnel.local_port}/aicategorymapping"
            new_env_lines.append(f'POSTGRES_CONNECTION_STRING={new_connection}\n')
        
        # Write updated .env
        with open('.env', 'w') as f:
            f.writelines(new_env_lines)
        
        print("✅ .env file updated for SSH tunnel")
        return True
        
    except Exception as e:
        print(f"❌ Failed to update .env file: {e}")
        return False

def main():
    print("🚀 SSH Tunnel Database Connection")
    print("=" * 50)
    
    tunnel = SSHTunnel()
    
    try:
        # Create SSH tunnel
        if not tunnel.create_tunnel():
            print("💥 Failed to create SSH tunnel")
            return False
        
        # Test database connection
        if not test_database_connection(tunnel):
            print("💥 Database connection test failed")
            return False
        
        # Update .env file
        if not update_env_for_tunnel(tunnel):
            print("💥 Failed to update .env file")
            return False
        
        print("\n" + "=" * 50)
        print("🎉 SSH tunnel setup completed successfully!")
        print(f"\n📋 Connection details:")
        print(f"   SSH Tunnel: {tunnel.ssh_user}@{tunnel.ssh_host}")
        print(f"   Local Port: {tunnel.local_port}")
        print(f"   Database: localhost:{tunnel.local_port}")
        print(f"\n⚠️  Keep this script running to maintain the tunnel!")
        print("   Press Ctrl+C to close the tunnel")
        
        # Keep tunnel alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Received interrupt signal")
        
    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        return False
    
    finally:
        tunnel.close_tunnel()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
