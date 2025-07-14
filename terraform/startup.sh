#!/bin/bash
set -e
apt-get update

cd /home/ubuntu

# AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
apt install -y unzip
unzip awscliv2.zip
sudo ./aws/install

# Docker
apt-get install -y ca-certificates curl gnupg lsb-release
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
apt update

# Docker
apt install -y docker-ce
usermod -aG docker ubuntu
docker --version >> /var/log/startup.log
docker compose version >> /var/log/startup.log

mkdir -p /home/ubuntu/.ssh
echo "${private_key}" > /home/ubuntu/.ssh/id_rsa
chmod 600 /home/ubuntu/.ssh/id_rsa

ssh-keyscan github.com >> /home/ubuntu/.ssh/known_hosts
chown -R ubuntu:ubuntu /home/ubuntu/.ssh

sudo -u ubuntu -i git clone -b "${branch}" --single-branch git@github.com:gqferreira/mqtt-mongo-python-private.git
cd mqtt-mongo-python-private

if [ "${environment}" = "prod" ]; then
    sudo -u ubuntu /usr/bin/docker compose -f docker-compose.prod.yml -p telemetry up -d --build
else
    sudo -u ubuntu /usr/bin/docker compose -f docker-compose.dev.yml -p telemetry up -d --build
fi

chown -R ubuntu:ubuntu /home/ubuntu/mqtt-mongo-python-private

# AWS CloudWatch Agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
dpkg -i amazon-cloudwatch-agent.deb

# AWS CloudWatch Agent Configuration
cat <<'EOF' > /opt/aws/amazon-cloudwatch-agent/bin/config.json
{
  "agent": {
    "metrics_collection_interval": 60,
    "logfile": "/opt/aws/amazon-cloudwatch-agent/logs/amazon-cloudwatch-agent.log",
    "run_as_user": "root"
  },
  "metrics": {
      "append_dimensions": {
      "InstanceId": "$${aws:InstanceId}"
    },
    "metrics_collected": {
      "cpu": {
        "measurement": ["cpu_usage_idle", "cpu_usage_user", "cpu_usage_system"],
        "metrics_collection_interval": 60,
        "totalcpu": true
      },
      "mem": {
        "measurement": ["mem_used_percent"],
        "metrics_collection_interval": 60
      }
    }
  }
}
EOF

# Start the CloudWatch Agent
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
  -a fetch-config \
  -m ec2 \
  -c file:/opt/aws/amazon-cloudwatch-agent/bin/config.json \
  -s

touch /home/ubuntu/finished.txt