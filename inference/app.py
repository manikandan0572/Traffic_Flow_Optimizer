
from pathlib import Path

import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from stable_baselines3 import PPO

app = FastAPI(title="Traffic Flow Optimizer API")

MODEL_PATH = Path(__file__).resolve().parents[1] / "ppo_traffic_model.zip"

model = None


def load_model():
    global model

    if model is None:
        print("Initializing model...")

        try:
            model = PPO.load(str(MODEL_PATH))
            print("Model loaded successfully.")
        except Exception as e:
            print(f"Error loading model: {e}")
            raise RuntimeError(f"Could not load model from {MODEL_PATH}") from e


class TrafficState(BaseModel):
    queues: list[float] = Field(min_length=4, max_length=4)
    current_phase: int = Field(default=0, ge=0, le=3)
    time_on_phase: int = Field(default=0, ge=0)


@app.on_event("startup")
async def startup_event():
    load_model()


@app.get("/")
def health_check():
    return {
        "status": "healthy",
        "message": "Traffic Flow Optimizer API is running."
    }


@app.post("/predict")
def predict_action(state: TrafficState):
    global model

    if model is None:
        load_model()

    try:
        queues = list(state.queues)

        one_hot = [
            1.0 if i == state.current_phase else 0.0
            for i in range(4)
        ]

        time_elapsed = [float(state.time_on_phase * 5.0)]

        obs = np.array(
            queues + one_hot + time_elapsed,
            dtype=np.float32
        )

        action, _ = model.predict(obs, deterministic=True)

        return {"phase": int(action)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
