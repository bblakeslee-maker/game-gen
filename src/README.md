

# Conda garbage

```bash
conda create -n game-gen python=3.10 pip
conda activate game-gen
conda install ffmpeg

pip install arcade python-dotenv openai numpy opencv-python
```

# Stable diffusion server setup
ssh into Darren's desktop

```
ssh user@172.30.0.94
```

cd into the automatic1111 repo

```
cd /home/vbanerjee/stable-diffusion-webui
```

Run the script to start the server

```
./webui.sh --allow-code --api --listen --port 7860
```