# Deploying Astra ML Assistant to Render

This project is ready to be deployed to [Render](https://render.com/) using Docker.

## Prerequisites
1.  A Render account.
2.  Your project uploaded to a GitHub repository.

## Deployment Steps

### Option 1: Using Render Blueprint (Recommended)
1.  Connect your GitHub repository to Render.
2.  Render will automatically detect the `render.yaml` file.
3.  Go to the **Blueprints** section in your Render Dashboard.
4.  Click **New Blueprint Instance**.
5.  Select your repository.
6.  In the **Environment Variables** section, make sure to set your `PERPLEXITY_API_KEY`.
7.  Click **Deploy**.

### Option 2: Manual Docker Deployment
1.  Create a new **Web Service** on Render.
2.  Connect your GitHub repository.
3.  Select **Docker** as the Runtime.
4.  In the **Advanced** section, add the following Environment Variables:
    -   `PERPLEXITY_API_KEY`: Your Perplexity API key.
    -   `PORT`: `8000` (Render will use this to route traffic).
5.  Click **Create Web Service**.

## Important Notes
- **Persistent Storage:** By default, Render's disk is ephemeral. This means your `backend/data/moonknight.db` and `logs/server.log` will be reset every time the service restarts. For production use, you should attach a **Render Disk** to the `/app/backend/data` and `/app/logs` paths.
- **Free Tier:** Render's free tier spins down after inactivity. The first request after a spin-down might take a few seconds as the container starts up.
