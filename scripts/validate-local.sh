#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$ROOT_DIR"

python3 -m py_compile files/plugins/check_memory.py files/plugins/check_zabbix_api.py
python3 -m json.tool inventory/lab.json >/dev/null
python3 -m unittest discover -s tests -v
bash -n scripts/validate-local.sh

if command -v ansible-playbook >/dev/null 2>&1; then
  ansible-playbook --syntax-check -i inventory/lab.json playbooks/validate.yml
  ansible-playbook --syntax-check -i inventory/lab.json playbooks/apply.yml
  ansible-playbook --syntax-check -i inventory/lab.json playbooks/configure-nrpe.yml
else
  printf '%s\n' "SKIP - ansible-playbook is not installed; Ansible syntax check was not run."
fi
