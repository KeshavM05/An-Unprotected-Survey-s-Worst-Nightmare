#!/bin/bash
echo "🛡️  Securing live stats.json..."
if [ -f stats.json ]; then
    cp stats.json stats_backup.json
fi

echo "🔄 Pulling latest updates from GitHub..."
git fetch
git reset --hard origin/main

echo "вос Restoring live stats.json..."
if [ -f stats_backup.json ]; then
    mv stats_backup.json stats.json
fi

echo "🚀 Restarting Survey Spammer background service..."
sudo systemctl restart spammer
echo "✅ Server gracefully updated to the latest code!"
