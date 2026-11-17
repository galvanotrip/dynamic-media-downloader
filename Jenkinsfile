pipeline {
    agent any

    parameters {
        string(name: 'URL', defaultValue: '', description: 'Enter the video URL to download')
    }

    stages {
        stage('🧪 Setup Python environment') {
            steps {
                sh '''
                    echo "🔧 Creating virtual environment..."
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('🚀 Download video') {
            steps {
                sh '''
                    echo "🎯 Downloading from URL: $URL"
                    . venv/bin/activate
                    python main.py "$URL"
                '''
            }
        }

        stage('📂 Move to SMB folder') {
            steps {
                sh '''
                    echo "📦 Moving finished .mp4 files to /var/smb/, keeping <channel>/<playlist>/ folders"
                    if [ ! -d downloads ]; then echo "⚠️ Nothing downloaded"; exit 0; fi
                    cd downloads
                    # skip yt-dlp intermediate streams like "name.f401.mp4" left by a failed merge
                    find . -type f -name '*.mp4' ! -name '*.f[0-9]*.mp4' -exec sh -c '
                        for f; do
                            mkdir -p "/var/smb/$(dirname "$f")" && mv -n "$f" "/var/smb/$f" && echo "  ✅ $f"
                        done' sh {} +
                    echo "ℹ️ mp4 left in workspace: $(find . -type f -name '*.mp4' | wc -l)"
                '''
            }
        }
    }

    post {
        success {
            echo '✅ Pipeline completed successfully. Video is available in /opt/smb.'
        }
        failure {
            echo '❌ Pipeline failed. Check the logs and verify the video URL.'
        }
        always {
            echo 'ℹ️ Pipeline finished.'
        }
    }
}