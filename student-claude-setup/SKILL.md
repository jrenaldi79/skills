---
name: student-claude-setup
description: Configures a student's local SSH client to connect to their remote Claude Code VPS securely. Use this when a student asks to set up their connection to their new server.
---

# Student Claude Setup

This skill automates the configuration of a student's local SSH client so they can easily and securely connect to their remote Virtual Private Server (VPS) where Claude Code is hosted. 

It handles copying their private key into a secure location, setting the strict permissions required by SSH, and setting up an SSH config alias that automatically attaches them to a persistent `tmux` session on the server.

## Prerequisites
- The student must have been assigned an IP address for their server.
- The student must have downloaded their private SSH key file to their local machine.

## Workflow

1. Ask the student for two pieces of information:
   - The IP address of their assigned server.
   - The local path to the private SSH key file they were given.
2. Run the included Python script to configure their system:
   ```bash
   python scripts/setup_ssh.py <ip_address> <path_to_key>
   ```
3. The script will automatically:
   - Copy their SSH key into their `~/.ssh/` directory.
   - Set the required `600` permissions on the key so SSH will accept it.
   - Add a `claude-box` alias to their `~/.ssh/config` file.
   - Configure the alias to automatically launch and attach to a persistent `tmux` session named `claude-session` upon connection.
   - Detect their Operating System and check if an RDP client is installed.
   - Generate a `Claude-Box-Visual.rdp` shortcut file directly on their Desktop.
   - Prompt the student to link their Google Drive for automatic code syncing.
   - Automatically execute a background connectivity test to ensure the SSH connection works, providing troubleshooting steps if it fails.
4. Instruct the student on their options to connect and work:
   - **Terminal:** Type `ssh claude-box`
   - **File Syncing:** Work inside the `projects/GoogleDrive` folder on the VPS to have code automatically sync to their local computer via Google Drive.
   - **Visual Desktop:** Double-click the newly created `Claude-Box-Visual.rdp` file on their Desktop and enter their visual password when prompted.

   - **File Editing:** Download Visual Studio Code, install the "Remote - SSH" extension, and connect to the `claude-box` host to browse files as if they were local.
   - **Claude Desktop:** Open the Claude Desktop app, select the "SSH" connection option, and enter `claude-box` as the Host to work with the AI agent directly on your server.
