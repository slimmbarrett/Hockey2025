# Telegram Hockey Predictor

## Structure

- `frontend/` - React WebApp (deploy to Vercel)
- `backend/` - FastAPI service (deploy to Render or Railway)
- Uses Supabase for DB, Telegram Bot API for notifications

## Setup

1. Set `.env` in backend with:
   - TELEGRAM_BOT_TOKEN=
   - SUPABASE_DB_URL=

2. Deploy backend to Railway/Render
3. Deploy frontend to Vercel
4. Insert SQL schema to Supabase

## Supabase SQL
```sql
create table users (
  user_id text primary key,
  name text,
  points integer default 0
);

create table matches (
  id serial primary key,
  teamA text,
  teamB text,
  date date,
  result jsonb
);

create table predictions (
  id serial primary key,
  user_id text references users(user_id),
  match_id integer references matches(id),
  score_a integer,
  score_b integer
);
```
