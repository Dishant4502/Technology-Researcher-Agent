// ─────────────────────────────────────────────────────────────────────────────
// Jenkinsfile – Declarative Pipeline for Technology Researcher Agent
// Compatible with Jenkins 2.400+ with the following plugins installed:
//   Docker Pipeline, Pipeline Utility Steps, Slack Notification,
//   JUnit, HTML Publisher, Credentials Binding
// ─────────────────────────────────────────────────────────────────────────────

pipeline {
    agent any

    // ── Tool versions (configure these names in Jenkins → Global Tool Config) ─
    tools {
        // Python managed by pyenv or system-level install
        // Node.js managed by NodeJS Jenkins plugin
        nodejs 'NodeJS-20'
    }

    environment {
        PYTHON_VERSION  = '3.12'
        REGISTRY        = 'ghcr.io'
        BACKEND_IMAGE   = "${REGISTRY}/${env.GITHUB_ACTOR ?: 'your-org'}/tech-researcher-backend"
        FRONTEND_IMAGE  = "${REGISTRY}/${env.GITHUB_ACTOR ?: 'your-org'}/tech-researcher-frontend"
        IMAGE_TAG       = "${env.GIT_COMMIT[0..6]}"
        // Credentials IDs – add these in Jenkins → Manage Credentials
        GHCR_CREDS      = credentials('ghcr-token')           // Username + PAT
        SLACK_CHANNEL   = '#deployments'
    }

    options {
        timeout(time: 30, unit: 'MINUTES')
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '20'))
        timestamps()
    }

    stages {

        // ── 1. Checkout ─────────────────────────────────────────────────────
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.GIT_AUTHOR = sh(returnStdout: true,
                        script: 'git log -1 --format="%an"').trim()
                    echo "Building commit ${IMAGE_TAG} by ${GIT_AUTHOR}"
                }
            }
        }

        // ── 2. Backend lint & test (parallel with frontend) ─────────────────
        stage('Quality Gates') {
            parallel {

                stage('Backend · Lint') {
                    steps {
                        dir('backend') {
                            sh '''
                                python${PYTHON_VERSION} -m venv .venv
                                . .venv/bin/activate
                                pip install --quiet --upgrade pip
                                pip install --quiet ruff
                                ruff check .
                                ruff format --check .
                            '''
                        }
                    }
                }

                stage('Backend · Tests') {
                    steps {
                        dir('backend') {
                            sh '''
                                python${PYTHON_VERSION} -m venv .venv
                                . .venv/bin/activate
                                pip install --quiet --upgrade pip
                                pip install --quiet -r requirements.txt
                                pip install --quiet pytest pytest-cov pytest-asyncio httpx
                                pytest -m "not integration" \
                                       --cov=app \
                                       --cov-report=xml:coverage.xml \
                                       --junitxml=test-results.xml \
                                       -v
                            '''
                        }
                    }
                    post {
                        always {
                            junit 'backend/test-results.xml'
                            recordCoverage(
                                tools: [[parser: 'COBERTURA', pattern: 'backend/coverage.xml']],
                                qualityGates: [[threshold: 50.0, metric: 'LINE', baseline: 'PROJECT']]
                            )
                        }
                    }
                }

                stage('Frontend · Build') {
                    steps {
                        dir('frontend') {
                            sh '''
                                npm ci --frozen-lockfile
                                npm run build
                            '''
                        }
                    }
                    post {
                        success {
                            archiveArtifacts artifacts: 'frontend/dist/**', fingerprint: true
                        }
                    }
                }

            } // end parallel
        }

        // ── 3. Docker build & push (only on main branch) ──────────────────────
        stage('Docker Build & Push') {
            when {
                branch 'main'
            }
            parallel {

                stage('Backend image') {
                    steps {
                        script {
                            docker.withRegistry("https://${REGISTRY}", 'ghcr-token') {
                                def img = docker.build(
                                    "${BACKEND_IMAGE}:${IMAGE_TAG}",
                                    "--file backend/Dockerfile backend"
                                )
                                img.push()
                                img.push('latest')
                            }
                        }
                    }
                }

                stage('Frontend image') {
                    steps {
                        script {
                            docker.withRegistry("https://${REGISTRY}", 'ghcr-token') {
                                def img = docker.build(
                                    "${FRONTEND_IMAGE}:${IMAGE_TAG}",
                                    "--file frontend/Dockerfile " +
                                    "--build-arg VITE_API_BASE=${env.VITE_API_BASE ?: '/api'} " +
                                    "frontend"
                                )
                                img.push()
                                img.push('latest')
                            }
                        }
                    }
                }

            } // end parallel
        }

        // ── 4. Deploy to production ──────────────────────────────────────────
        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                // ── Render.com webhook deploy ────────────────────────────────
                withCredentials([
                    string(credentialsId: 'render-hook-backend',  variable: 'RENDER_BACKEND'),
                    string(credentialsId: 'render-hook-frontend', variable: 'RENDER_FRONTEND')
                ]) {
                    sh 'curl -sSf -X POST "$RENDER_BACKEND"'
                    sh 'curl -sSf -X POST "$RENDER_FRONTEND"'
                }

                // ── Alternative: SSH deploy to EC2 ───────────────────────────
                // Uncomment if you prefer EC2:
                // sshagent(['ec2-deploy-key']) {
                //     sh """
                //         ssh -o StrictHostKeyChecking=no ${EC2_USER}@${EC2_HOST} '
                //             docker pull ${BACKEND_IMAGE}:${IMAGE_TAG}
                //             docker service update \\
                //               --image ${BACKEND_IMAGE}:${IMAGE_TAG} \\
                //               --update-failure-action rollback \\
                //               tech-researcher_backend
                //         '
                //     """
                // }
            }
        }

        // ── 5. Smoke test ────────────────────────────────────────────────────
        stage('Smoke Test') {
            when {
                branch 'main'
            }
            steps {
                sleep 30
                sh '''
                    HTTP=$(curl -s -o /dev/null -w "%{http_code}" \
                        "${PRODUCTION_API_URL}/health")
                    echo "Health check HTTP status: $HTTP"
                    [ "$HTTP" = "200" ] || exit 1
                '''
            }
        }

    } // end stages

    post {
        success {
            slackSend(
                channel: env.SLACK_CHANNEL,
                color: 'good',
                message: """✅ *${currentBuild.fullDisplayName}* succeeded.
Branch: `${env.BRANCH_NAME}` | Tag: `${IMAGE_TAG}` | Author: ${GIT_AUTHOR}
<${env.BUILD_URL}|View build>"""
            )
        }
        failure {
            slackSend(
                channel: env.SLACK_CHANNEL,
                color: 'danger',
                message: """🚨 *${currentBuild.fullDisplayName}* FAILED.
Branch: `${env.BRANCH_NAME}` | Author: ${GIT_AUTHOR}
<${env.BUILD_URL}|View build>"""
            )
        }
        always {
            cleanWs()
        }
    }
}
