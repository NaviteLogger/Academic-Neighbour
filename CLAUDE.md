# Repository Instructions for Claude Code

## Workflow & Communication
1. **Verify Before Acting:** Always verify the current state of files, dependencies, and logs before proposing a solution. 
2. **Accurate Status Checks:** Ensure accurate exit codes by executing direct status commands (e.g., `gh run view`). Avoid reading exit codes through piped or backgrounded wrappers (e.g., `gh run watch ... | tail`).
3. **Architecture Check:** Confront the user with proposed architectural solutions for approval before writing generic setup code.
4. **Categorize Output:** Always separate and label your responses using this exact format:
   - **Observed:** Facts directly verified from files, commands, or runtime.
   - **Unknown:** Information not yet established.
   - **Proposal:** An option requiring user approval.
   - **Approved:** Code/actions to implement only after user approval.

## Environment & Connectivity
1. **Shell Context:** The local user environment requires `zsh` formatting. Format remote VM shell commands for `bash`. 
2. **Autonomous SSH Verification:** Connect to the private VM subnet (`10.10.0.0/24`) directly from this devcontainer to verify issues yourself before asking the user.
3. **VPN & Connection:** Verify the VPN status with `ip addr show navite`. If required, initiate it using `sudo wg-quick up .ssh/wireguard/navite.conf`. Connect via `ssh -i .ssh/vm_ops_admin_ed25519 -o IdentitiesOnly=yes ops-admin@<private-ip>` (reference `docs/troubleshooting/vpn-and-ssh.md`).
4. **Network Troubleshooting:** Host-specific TCP restrictions exist (e.g., the public edge host accepts only 443 from Cloudflare). If a connection times out, test another known-good host before assuming a broken VPN.
5. **Host-Specific Commands:** Provide explicit connection details (user, key, proxy) for the specific host when handing commands to the user. Acknowledge distinct credentials for different classes (e.g., Proxmox uses `ansible-admin`/`ansible_admin_ed25519`; VMs use `ops-admin`/`vm_ops_admin_ed25519`).

## Infrastructure & Deployment
1. **Rolling Upgrades:** Apply restart-inducing changes to High Availability nodes (`vm-k3s-01`/`vm-k3s-02` and `edge-01`/`edge-02` behind VIP `10.10.0.190`) sequentially. Complete the change on one node and verify full health (Node Ready and application-level checks) before proceeding to the peer. Reference `docs/runbooks/rolling-node-upgrades.md`.
2. **Single-Instance Hosts:** Secure direct approval before applying changes to non-redundant hosts (`seaweedfs-01`, `openbao-01`, `kafka-01`, `btcpay-01`, `viewerboosts-01`).

## Code Quality & Style
1. **Simplicity:** Utilize functionality already provided by the existing stack. Write concise, idiomatic code. Use clean technical language.
2. **Absolute Paths Only:** Resolve the real path or value from the repo or live system. State explicitly and ask the user if a path cannot be resolved. Placeholder paths (e.g., `/path/to/cert`) are forbidden.
3. **Grammar:** Use positive phrasing. Avoid "X, not Y" grammatical structures.

## Dependency Management & CI
1. **Immutable Dependencies:** Dependency and library versions selected by `build.sh` are strict compatibility requirements. Maintain current versions. Propose upgrades only if strictly necessary, and implement them only after explicit repository-owner approval and compatibility testing.
2. **CI Accountability:** Immediately investigate and fix any GitHub Actions workflow failures triggered by your commits.

## Security Boundaries
*Note: To mathematically guarantee the agent cannot read these files, ensure they are listed in your `.gitignore`.*
1. **Restricted Files:** Ignore and completely avoid reading `.env` (unless it contains `.example`), `./ansible/vars/*.yml` (unless it contains `.example`), `*.tfvars`, `.pgpass`, and `.pg_service.conf`.