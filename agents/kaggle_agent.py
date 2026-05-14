import os
import pandas as pd
from agents.base_agent import BaseAgent

class KaggleAgent(BaseAgent):
    def __init__(self, memory_manager, model_router=None):
        super().__init__(name="KaggleAgent", memory_manager=memory_manager, model_router=model_router)
        self.data_dir = "/home/kizabgd/.gemini/tmp/memorijada/data/"

    def load_data(self, filename):
        path = os.path.join(self.data_dir, filename)
        if not os.path.exists(path):
            raise FileNotFoundError(f"File {filename} not found in {self.data_dir}")
        if filename.endswith('.csv'):
            return pd.read_csv(path)
        elif filename.endswith('.parquet'):
            return pd.read_parquet(path)
        else:
            raise ValueError(f"Unsupported file format: {filename}")

    async def execute(self, context: dict, trace_id: str):
        action = context.get("action")
        self.log_action(trace_id, "kaggle_action_start", {"action": action})
        
        try:
            if action == "load_train":
                df = self.load_data("train.csv")
                return {"status": "success", "rows": len(df)}
            elif action == "load_test":
                df = self.load_data("test.csv")
                return {"status": "success", "rows": len(df)}
            else:
                return {"status": "error", "error": f"Unknown action: {action}"}
        except Exception as e:
            self.log_action(trace_id, "kaggle_action_failed", {"error": str(e)})
            return {"status": "error", "error": str(e)}
