# execution_server
Step execution service for ingenium.

This service uses a pool of Python worker processes to execute steps.


### API
REST API is defined in execution.yaml

### Environment Variables
Following environment variables need to be set.
 * REDIS_HOST=execution_redis
 * REDIS_PORT=6379
 * JWT_SECRET=${JWT_SECRET}  
     
### How to run in local Docker environment

1. Check out following projects at the same directory level

 * Ingenium/execution_server
 * Ingenium/execution-dep
 
2. Set environment variables if needed. The env variables are set in docker-compose.yml. 
 
3. Build Docker images and run 
 
```bash
cd execution-dep/compose_single_node
sudo -E ./run_compose.sh up execution_server
```

### How to run in Swarm Deployment
```bash
make
```

### To run tests
1. Run test example.

```bash
pip install -r image/requirements.txt
virtualenv ve
source ve/bin/activate
cd tests
python execution_server_test.py

```