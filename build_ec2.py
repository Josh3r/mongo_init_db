import boto3
import os 
import subprocess
import paramiko
import time

client = boto3.client('ec2',
aws_access_key_id="ASIAVALDSCK5WAQRYQL7",
aws_secret_access_key="ZDMDtIp6lD5Fxd7nx+NcrgKtOZqkElgmCjU6qs0k",
aws_session_token="FwoGZXIvYXdzEF0aDHk2SkQ8Das5CB0FBiLNASMu4QwddCyjyv1rJfjNgZP3NliwWF37PH/BlPyvHJN4CA5l/od2mNaa/leTBdH8SCoClfd4wqTQ3nnlx81YvpCk9sgFpat53CBhJMWTX5TFzMak5akihVvQ0hoaWTsumUzqzM/y3bTP1sy5d81OXxvnqkJ1nVUkmokonC04fQMkzW6DFDK6iSpEO93f0Cqy109OE9h8XDDrMUiOtsLYwLaK3O1XmxG1Y1Euy+gJo4rZ81CVAnli6o2A7CHQZsPSsWEElJ4AdhZX42YrjgYovcOo/gUyLUMqWFxwiOzxV1Ws5gR7uzLRI027rtDqSxQ+PXGSzFZRPxOyd/lsllawP89GOw==",
region_name="us-east-1")

#create key
pem_file = open("key_pair.pem", "w")
keyname = "testes34"
keypair = client.create_key_pair(KeyName=keyname)
#print(keypair['KeyMaterial'])
pem_file.write(keypair['KeyMaterial'])
pem_file.close()
#

response = client.describe_vpcs()
vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')

try:
    #create security group
    response = client.create_security_group(GroupName='testes34',  
                                         Description='make descriptions great again',
                                         VpcId=vpc_id)

    #get security group id
    security_group_id = response['GroupId']

    
    data = client.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[
            {'IpProtocol': 'tcp',
             'FromPort': 80,
             'ToPort': 80,
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            {'IpProtocol': 'tcp',
             'FromPort': 22,
             'ToPort': 22,
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            {'IpProtocol': 'tcp',
            'FromPort': 27017,
            'ToPort': 27017,
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
        ])
    #print('Ingress Successfully Set %s' % data)
except Exception as e:
    print(e)
#

response = client.run_instances(ImageId='ami-00ddb0e5626798373',
                                InstanceType='t2.micro',
                                MinCount=1,
                                MaxCount=1,
                                KeyName=keyname,
                                SecurityGroupIds=[security_group_id]
                                )
#print(response)
created_instance = response["Instances"][0]
instance_id = created_instance["InstanceId"]
# Get information for all running instances
# Connect to EC2
s = boto3.Session(aws_access_key_id="ASIAVALDSCK5WAQRYQL7",
aws_secret_access_key="ZDMDtIp6lD5Fxd7nx+NcrgKtOZqkElgmCjU6qs0k",
aws_session_token="FwoGZXIvYXdzEF0aDHk2SkQ8Das5CB0FBiLNASMu4QwddCyjyv1rJfjNgZP3NliwWF37PH/BlPyvHJN4CA5l/od2mNaa/leTBdH8SCoClfd4wqTQ3nnlx81YvpCk9sgFpat53CBhJMWTX5TFzMak5akihVvQ0hoaWTsumUzqzM/y3bTP1sy5d81OXxvnqkJ1nVUkmokonC04fQMkzW6DFDK6iSpEO93f0Cqy109OE9h8XDDrMUiOtsLYwLaK3O1XmxG1Y1Euy+gJo4rZ81CVAnli6o2A7CHQZsPSsWEElJ4AdhZX42YrjgYovcOo/gUyLUMqWFxwiOzxV1Ws5gR7uzLRI027rtDqSxQ+PXGSzFZRPxOyd/lsllawP89GOw==",
region_name="us-east-1")
ec2 = s.resource('ec2')

# Get instance
instance = ec2.Instance(id=instance_id)
instance.wait_until_running() # Wait
current_instance = list(ec2.instances.filter(InstanceIds=[instance_id]))
ip_address = current_instance[0].public_ip_address
print("IP Address is:",ip_address)

# SSH func
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
def ssh_connect_with_retry(ssh, ip_address, retries):
    if retries > 3:
        return False
    privkey = paramiko.RSAKey.from_private_key_file(
        'key_pair.pem')
    interval = 5
    try:
        retries += 1
        print('SSH into the instance: {}'.format(ip_address))
        ssh.connect(hostname=ip_address,
                    username='ubuntu', pkey=privkey)
        return True
    except Exception as e:
        print(e)
        time.sleep(interval)
        print('Retrying SSH connection to {}'.format(ip_address))
        ssh_connect_with_retry(ssh, ip_address, retries)

# Now ssh in
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

ssh_connect_with_retry(ssh, ip_address, 0)
command1 = "yes"
stdin, stdout, stderr = ssh.exec_command(command1)
time.sleep(1) # wait
command2 = "wget https://raw.githubusercontent.com/Josh3r/mongo_init_db/main/setup_mongo.sh" # get my shell
stdin, stdout, stderr = ssh.exec_command(command2)
time.sleep(1)
command3 = "bash setup_mongo.sh"
stdin, stdout, stderr = ssh.exec_command(command3)
# Get information for all running instances
"""
running_instances = ec2.instances.filter(Filters=[{
    'Name': 'instance-state-name',
    'Values': ['running']}])
for instance in running_instances:
    host = instance.public_ip_address
print(host)
"""
# ssh
# subprocess.Popen("ssh ubuntu@{host} -i {key_dir}".format(host=host, key_dir='\key_pair.pem'), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()