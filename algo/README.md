# Algo / Simulator

## Setup:

1. Clone this repo
2. Run the following commands in terminal
3. For the backend running the algo:

```
cd algo/server
pip install flask-cors python-tsp
python server.py
```

4. Backend should be running on http://localhost:5000, open http://localhost:5000/status to check server status
5. Open another concurrent terminal for the frontend and run:

```
cd algo/simulator-client
npm i
npm run dev
```

6. Simulator should be running on http://localhost:3000