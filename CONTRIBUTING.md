````markdown
# Contributing to AgentCore Examples

Thanks for contributing! Here's how to do it properly.

---

## Workflow

1. **Fork** the repo
2. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/your-example-name
   ```
3. Make your changes
4. Test locally before pushing
5. Submit a **Pull Request**

---

## Branch Naming

| Type | Format | Example |
|---|---|---|
| New example | `feature/example-name` | `feature/memory-agent` |
| Bug fix | `fix/description` | `fix/browser-session-timeout` |
| Docs | `docs/description` | `docs/setup-instructions` |

---

## Adding a New Example

1. Create a new folder: `your-example-name/`
2. Add these files:

```
your-example-name/
├── README.md        ← Required!
├── agent.py
└── requirements.txt
```

3. Update the root `README.md` table
4. Never commit `.env` files!

---

## Rules

- ✅ Always test locally before submitting a PR
- ✅ Always update the README for your example
- ✅ Never commit `.env` or credentials
- ✅ Keep examples self-contained
- ✅ Follow existing code style
- ❌ Don't push directly to `main`
- ❌ Don't hardcode AWS credentials

---

## Repo Protections Summary

| Protection | What it does |
|---|---|
| Branch rules | No direct pushes to `main` |
| PR template | Ensures changes are documented |
| GitHub Actions | Auto-checks for secrets and syntax errors |
| `CONTRIBUTING.md` | Clear guidelines for contributors |

This ensures:

- ✅ No one can break `main` directly
- ✅ All changes are reviewed
- ✅ No accidental secret commits
- ✅ Code syntax is always valid
````