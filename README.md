# Manim AI Visualiser

AI-powered tool that generates Manim animations for DSA concepts.

---

## Table of Contents
1. [Setup](#1-setup)
2. [Cloning the Repo](#2-cloning-the-repo)
3. [Your Branch](#3-your-branch)
4. [Making Changes](#4-making-changes)
5. [Pushing Your Work](#5-pushing-your-work)
6. [Golden Rules](#6-golden-rules)

---

## 1. Setup

Make sure you have these installed before starting:

- [Git](https://git-scm.com/downloads)
- [Python 3.10+](https://www.python.org/downloads/)

Then install project dependencies:

```bash
pip install -r requirements.txt
```

Copy the environment variables file and fill in your values:

```bash
cp .env.example .env
```

> Never share or commit your `.env` file. It is already gitignored.

---

## 2. Cloning the Repo

Run this once on your machine to download the project:

```bash
git clone <repo-url>
cd manim_ai_visualiser
```

---

## 3. Your Branch

Each person works on their own branch. **Do not work on `main`.**

| Person | Branch |
|--------|------------------|
| Person 1 (Knowledge Base) | `feature/KB` |
| Person 2 (AI Agents) | `feature/ai` |
| Person 3 & 4 (Streamlit UI) | `feature/streamlit` |

After cloning, switch to your branch:

```bash
git checkout feature/your-branch-name
```

Example:

```bash
git checkout feature/KB
```

To confirm which branch you are on:

```bash
git branch
```

The branch with a `*` next to it is your current one.

---

## 4. Making Changes

**Always follow this order before you start working:**

### Step 1 — Pull the latest changes

This keeps your branch up to date:

```bash
git pull origin feature/your-branch-name
```

### Step 2 — Make your changes

Edit your files as needed in your code editor.

### Step 3 — Check what you changed

```bash
git status
```

This shows which files have been modified.

### Step 4 — Stage your changes

To stage specific files (recommended):

```bash
git add filename.py
```

Or to stage everything you changed:

```bash
git add .
```

### Step 5 — Commit with a clear message

```bash
git commit -m "short description of what you did"
```

Good commit message examples:
- `"add binary search scene to knowledge base"`
- `"fix retriever returning wrong results"`
- `"implement scene plan table in UI"`

Bad commit message examples:
- `"changes"`
- `"fix"`
- `"asdfgh"`

---

## 5. Pushing Your Work

Once you have committed, push to **your branch only**:

```bash
git push origin feature/your-branch-name
```

Example:

```bash
git push origin feature/KB
```

> If this is your first push on a branch, git may ask you to set an upstream. Just run the command it suggests — it usually looks like `git push --set-upstream origin feature/your-branch-name`.

---

## 6. Golden Rules

- **Never push to `main`** — main is protected and is merged into by the team lead only
- **Never work on someone else's branch** without telling them first
- **Pull before you start working** every single time — this prevents conflicts
- **Commit often** — small focused commits are easier to review and undo than one large one
- **Never commit your `.env` file** — it contains secrets that must stay local
- **Write clear commit messages** — your teammates need to understand what you did

---

## Project Structure

```
manim_ai_visualiser/
├── app.py                        # Streamlit UI entry point
├── config.py                     # Environment variables & constants
├── requirements.txt              # Python dependencies
├── .env.example                  # Template for your .env file
├── agents/
│   ├── prompt_expander.py        # AI 1: generates scene plan JSON
│   ├── manim_coder.py            # AI 2: generates Manim code per scene
│   └── prompts/
│       ├── expander_system.txt   # System prompt for AI 1
│       └── coder_system.txt      # System prompt for AI 2
├── knowledge_base/
│   ├── retriever.py              # RAG: fetches relevant scenes
│   ├── embeddings/
│   │   ├── schema.sql            # Supabase pgvector table setup
│   │   └── embed.py              # One-time script to embed scenes
│   ├── problems/                 # Python DSA solutions
│   └── scenes/                   # Paired Manim scene files
├── pipeline/
│   ├── executor.py               # Runs manim render via subprocess
│   ├── stitcher.py               # FFmpeg concat to final.mp4
│   └── session.py                # Orchestrates the full pipeline
├── ui/
│   └── components.py             # Reusable Streamlit components
└── outputs/                      # Generated video clips (gitignored)
```
