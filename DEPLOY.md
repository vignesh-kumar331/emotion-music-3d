# Live Deploy
Frontend: Vercel — Import https://github.com/vignesh-kumar331/emotion-music-3d, root \rontend\, build \
pm run build\, output \dist\
Backend: Render — New Web Service from same repo, root \ackend\, build \pip install -r requirements.txt\, start \uvicorn app.main:app --host 0.0.0.0 --port \\
Env: SECRET_KEY (generate), DATABASE_URL sqlite or Postgres
