from __future__ import annotations

import json
import sys

from .inference_service import predict_rul


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: python -m src.predictive_layer.predict <payload.json>")
    payload = json.loads(open(sys.argv[1], "r", encoding="utf-8").read())
    print(json.dumps(predict_rul(payload), indent=2))


if __name__ == "__main__":
    main()
