#!/usr/bin/env bash

# Git commands to add and push
git add docs README.md pyproject.toml Dockerfile docker-compose.yml src tests scripts infra
git commit -m "Add OpenCode docs + API scaffold"
git push origin main

