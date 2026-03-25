# Complete Setup Guide
## AWS Bedrock AgentCore Examples — macOS

---

## Part 1: Install Required Software

### 1.1 Install Python

1. Go to https://www.python.org/downloads
2. Click **Download Python 3.12**
3. Open the downloaded file and follow the installer

Verify the installation:
```bash
python3 --version
# Should show: Python 3.12.x
```

### 1.2 Install Git

```bash
xcode-select --install
```

Click **Install** when prompted.

### 1.3 Install an IDE

- **Cursor** (recommended): https://cursor.sh
- **VS Code**: https://code.visualstudio.com

---

## Part 2: AWS Setup

### 2.1 Create IAM Role for Browser Tool

The browser tool needs an IAM role to access AWS services.

1. Go to **AWS Console → IAM → Roles**
2. Click **Create role**
3. Search for and attach these managed policies:
   - AmazonBedrockFullAccess
   - CloudWatchFullAccess
   - AWSXRayFullAccess
   - AmazonS3FullAccess
   - AWSXRayDaemonWriteAccess
   - BedrockAgentCoreFullAccess
4. Click **Next**
5. Set the role name to `agentcore-browser-role`
6. Click **Create role**
7. Click on the role you just created and copy the **Role ARN**:
```
arn:aws:iam::YOUR_ACCOUNT:role/agentcore-browser-role
```

### 2.2 Create IAM User

1. Go to **AWS Console → IAM → Users**
2. Click **Create user**
3. Set the username to `agentcore-user`
4. Click **Next**
5. Select **Attach policies directly**
6. Search for and attach these managed policies:
   - AmazonBedrockFullAccess
   - CloudWatchFullAccess
   - AWSXRayFullAccess
   - AmazonS3FullAccess
   - AWSXRayDaemonWriteAccess
   - BedrockAgentCoreFullAccess
7. Click **Next → Create user**

### 2.3 Create Access Keys

1. Click on your user
2. Click the **Security credentials** tab
3. Scroll to **Access keys** and click **Create access key**
4. Select **Local code**
5. Click **Next → Create access key**
6. **Copy both keys now — you won't be able to see them again:**
   - `Access key ID` → your `AWS_ACCESS_KEY_ID`
   - `Secret access key` → your `AWS_SECRET_ACCESS_KEY`
7. Click **Done**

### 2.4 Enable CloudWatch Transaction Search

1. Go to **AWS Console → CloudWatch → Settings**
2. Find **Transaction Search** and click **Edit**
3. Enable **Ingest spans as structured logs in OpenTelemetry format**
4. Click **Save**

---

## Part 3: Get the Code

```bash
git clone https://github.com/nirbhay-agarwal/agentcore-examples.git
cd agentcore-examples
```

---

## Part 4: Python Environment

```bash
# Make sure you are in the root folder
cd agentcore-examples

# Create a virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# You should see (venv) in your terminal prompt
```

---

Now follow the setup instructions inside each example folder.
```