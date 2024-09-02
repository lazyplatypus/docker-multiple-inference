# Docker Multiple Inference

This project sets up a Streamlit application that compares responses from a local Llama model (using Ollama) and a Cerebras-hosted model side by side, all running within Docker containers.

## Prerequisites

- Docker
- A Cerebras API key (obtain from cloud.cerebras.ai)

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/docker-multiple-inference.git
   cd docker-multiple-inference
   ```

2. **Set up Ollama with Llama model:**
   ```bash
   docker pull ollama/ollama
   docker run -d --gpus=all -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
   docker exec -it ollama ollama run llama3:8b
   ```

3. **Pull the Cerebras Cloud SDK Docker image:**
   ```bash
   docker pull cerebras/cerebras-cloud-sdk
   ```

4. **Set up Cerebras environment:**
   ```bash
   export CEREBRAS_API_KEY="your-api-key-here"
   ```

5. **Create a file named `requirements.txt` with the following content:**
   ```
   streamlit
   requests
   aiohttp
   ```

6. **Create a file named `app.py` and paste the Python code for the dual-model chatbot into it.**
   (Use the latest version of the code provided in the previous response)

7. **Create a `Dockerfile` with the following content:**
   ```dockerfile
   FROM cerebras/cerebras-cloud-sdk

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY app.py .

   EXPOSE 8501

   CMD ["streamlit", "run", "app.py"]
   ```

8. **Build the Docker image:**
   ```bash
   docker build -t docker-multiple-inference .
   ```

9. **Run the Docker container:**
   For macOS and Windows:
   ```bash
   docker run -p 8501:8501 -e CEREBRAS_API_KEY=$CEREBRAS_API_KEY docker-multiple-inference
   ```
   For Linux:
   ```bash
   docker run -p 8501:8501 --add-host=host.docker.internal:host-gateway -e CEREBRAS_API_KEY=$CEREBRAS_API_KEY docker-multiple-inference
   ```

10. **Access the application:**
    Open a web browser and go to `http://localhost:8501`

## Usage

- Enter your prompt in the text input field at the bottom of the page.
- The responses from both the local Llama model and the Cerebras model will appear side by side in real-time.
- The conversation history is maintained for the local model to provide context in subsequent interactions.

## Troubleshooting

- If you encounter issues with the local Llama model, ensure that the Ollama container is running and the model is properly loaded.
- For Cerebras API issues, verify that your API key is correctly set and that you have an active subscription.
- If the Streamlit app fails to start, check the Docker logs:
  ```bash
  docker logs $(docker ps -q --filter ancestor=docker-multiple-inference)
  ```

## Note

This setup uses the `host.docker.internal` DNS name to allow the Streamlit app container to communicate with the Ollama container on the host machine. This works out of the box for Windows and macOS. For Linux, we use the `--add-host` flag to enable this functionality.

## Contributing

Contributions to improve docker-multiple-inference are welcome. Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).