# live-ocr-consumers

Consumers for [live-ocr](https://github.com/<you>/live-ocr). live-ocr reads screen regions and posts them to a consumer. The consumer replies with a decision and the reasoning behind it, and live-ocr shows that reply in its log.

Requires live-ocr with snapshot events and consumer replies.

## Run

```bash
python serve.py example 8000
python serve.py --dir ../my-consumers my_consumer 8001   # a consumer kept in another folder
```

In live-ocr, open **Outputs...**, set the webhook to `http://127.0.0.1:8000/` with a cooldown of 0, and tick **Send one snapshot of all regions per pass**.

## Writing a consumer

A consumer is a Python module with `handle(event)`. Start by copying `example.py`.

The input is a live-ocr snapshot:

```json
{"v": 1, "type": "snapshot", "ts": "2026-09-15T02:19:55+00:00", "profile": "Default",
 "regions": {"Status": "Build passed", "Counter": "42"}}
```

Return `None` to ignore an event, or a reply in this format:

| Field | Meaning |
| --- | --- |
| `v` | Reply format version, currently `1`. |
| `consumer` | Name shown in live-ocr's log. |
| `in_reply_to` | The snapshot's `ts`. |
| `message` | One line for the user. The only field live-ocr requires. |
| `decision` | Machine-readable result, at least `action`. Future live-ocr actions will act on this. |
| `reason` | Why this decision was made. |
| `algorithm` | `name`, `version` and any parameters that produced the decision. |
| `inputs` | The values the decision was based on. |
| `warnings` | What the consumer could not read or does not handle. |

Keep `handle` fast. live-ocr waits up to 5 seconds for the reply.
