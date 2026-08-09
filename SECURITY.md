# Security Model

## Protected assets

- Files outside the selected repository root
- Environment files, private keys and certificate containers
- Model API credentials
- User changes that predate the current Agent run
- Integrity of validation results and audit records

## Enforced controls

- All file paths are canonicalized and must remain below the repository root.
- `.git`, `.repoagent`, dependency/build directories, symlinks and sensitive filename patterns are excluded.
- Context retrieval indexes only files admitted by the same path, sensitivity, size and encoding policy as direct reads.
- Existing files can only be changed through a unique exact-text replacement.
- New-file creation cannot overwrite an existing file.
- Changed-file count and file size are bounded.
- Commands are parsed with `shlex` and executed without a shell.
- Only configured test and lint command prefixes are accepted.
- Check subprocesses receive a reduced environment without model credentials.
- File writes and command execution require separate user capabilities.
- API writes and checks are disabled unless server operators opt in.
- The final observed validation failure overrides a model claim of completion.
- Original files are backed up once per run and can be restored without destructive Git operations.

## Threats covered by tests

- `../` path traversal
- Sensitive `.env` variants
- Non-allowlisted network/shell commands
- Repeated invalid tool actions
- Ambiguous text replacement
- Completion after failed validation
- Restoring modified and newly created files
- API write attempts while writes are disabled

## Out of scope

The command allowlist is not an operating-system sandbox. Tests and build tools can execute arbitrary repository code under the current user account. A hostile repository could access readable local files or the network even when the command itself is allowlisted.

For untrusted repositories, run the whole service in a disposable VM or hardened container with:

- No host credentials mounted
- Network disabled unless the model gateway is separately proxied
- Read-only root filesystem
- Dedicated writable repository volume
- CPU, memory, process and time limits
- Seccomp/AppArmor or an equivalent platform policy

The provided container is a packaging and deployment baseline, not a complete hostile-code sandbox.

## Reporting

Do not include secrets or a private repository in a public issue. Provide a minimal reproduction using synthetic files and the relevant redacted trace events.
