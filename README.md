# Kind Echo 🌙

Leave a voice note, receive a kind one from a stranger.

- **Your note is never stored**: it is released as soon as you record it.
- **You receive a kind voice note** left by an earlier visitor (only owner-approved notes are played),
  or a built-in encouraging message read aloud by your browser.
- **Pay it forward**: record a kind note for the next stranger. It waits for owner review before anyone hears it.
- **Report button** removes a note immediately for review.

## Run locally
```
pip install -r requirements.txt
python -m streamlit run app.py
```
Create `.streamlit/secrets.toml` with `ADMIN_PASSWORD = "your-password"` to use the review panel (sidebar).

## Deploy on Streamlit Community Cloud
1. Push `app.py`, `requirements.txt`, `README.md` and `.streamlit/config.toml` to a GitHub repo
   (do **not** upload `secrets.toml`).
2. On share.streamlit.io → Create app → pick the repo and `app.py`.
3. In the app's **Settings → Secrets**, add: `ADMIN_PASSWORD = "your-password"`.

**Note:** Streamlit Cloud's disk is temporary — saved kind notes are lost when the app restarts or redeploys.
For permanent storage, connect a database / cloud bucket.
