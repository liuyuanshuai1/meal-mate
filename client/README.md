# MealMate Mini Program

This directory contains the native WeChat Mini Program frontend.

## Local Setup

Create local config files from the public templates:

```bash
cp config.example.js config.js
cp project.config.example.json project.config.json
```

Then open this `client/` directory in WeChat Developer Tools.

## Config Files

- `config.js`: local runtime config used by the app. Keep it uncommitted.
- `config.example.js`: public template for local development.
- `project.config.json`: local WeChat Developer Tools project config. Keep it uncommitted.
- `project.config.example.json`: public template with a placeholder `appid`.
- `project.private.config.json`: personal WeChat Developer Tools preferences. Keep it uncommitted.

Important fields:

- `apiBaseUrl`: backend API base URL, usually `http://127.0.0.1:8000/api` for local development.
- `fixedUserId`: placeholder user ID used by the current frontend flow.
- `fixedPerson`: placeholder person key used by dinner records.

## Tests

Run frontend utility tests from this directory:

```bash
node --test tests/*.test.js
```
