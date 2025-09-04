# 雨云自动签到 (GitHub Action 版)

[![每日签到](https://github.com/xlxzhc/rainyun_autosignin/actions/workflows/signin.yml/badge.svg)](https://github.com/xlxzhc/rainyun_autosignin/actions/workflows/signin.yml)

本项目通过 GitHub Action 实现雨云每日自动签到。针对雨云更新后需要人机认证的问题，脚本已适配通用验证码服务。

## 特性

-   **零成本**: 完全基于免费的 GitHub Action 运行。
-   **安全**: 使用账户密码登录，不依赖可能泄露个人信息的 API Key。所有敏感信息均存储在 GitHub Secrets 中。
-   **灵活**: 支持通过环境变量自定义验证码识别服务。
-   **自动化**: 设置后每日自动执行，无需人工干预。

## 如何使用

### 1. Fork 本仓库

点击本页面右上角的 **Fork** 按钮，将此项目复制到你自己的 GitHub 账户下。

### 2. 配置 Secrets

在你 Fork 的仓库中，进入 `Settings` -> `Secrets and variables` -> `Actions`，点击 `New repository secret` 添加以下密钥：

#### 必填项

本项目不再提供默认验证码服务，您必须配置自己的验证码识别服务。

| Secret 名          | 描述                                                       | 示例                               |
| ------------------ | ---------------------------------------------------------- | ---------------------------------- |
| `YYQD`             | 雨云的**账户**和**密码**，用 `&` 分隔。多账户用 `#` 分隔。 | `your_email&your_password`         |
| `CAPTCHA_URL`      | 验证码识别接口的 URL。                                     | `https://api.example.com/solve`    |
| `CAPTCHA_METHOD`   | 请求验证码接口使用的方法，`GET` 或 `POST`。                | `POST`                             |
| `CAPTCHA_DATA`     | 发送到验证码接口的 JSON 数据。                             | `'{"key": "YOUR_API_KEY"}'`         |

> **注意**: `CAPTCHA_DATA` 必须是**单引号**包裹的合法 JSON 字符串，以便于在 GitHub Actions 工作流中正确解析。

### 3. 启用并运行 Action

1.  进入你仓库的 **Actions** 标签页，如果有提示，请点击按钮启用 GitHub Actions。
2.  在左侧列表中找到 **Rainyun Auto Signin** 工作流。
3.  点击 **Run workflow**，然后再次点击绿色的 **Run workflow** 按钮即可手动触发一次签到任务。
4.  之后，工作流将根据预设的 `cron` 计划（默认为每天早上 6:00 北京时间）自动运行。
