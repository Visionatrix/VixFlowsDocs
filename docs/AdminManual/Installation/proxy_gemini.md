# HTTP Proxy for Google Gemini API Access

This guide will help you set up an HTTP/HTTPS proxy to use the Google Gemini API.

This is useful if you're in a region where **free direct access** to the Gemini API is restricted.

!!! warning

    For **most** countries in the world you don't need this guide!

    If you use **Gemini Pro** model - you don't need it either, it doesn't have free access, and **paid access works** from everywhere and **without** proxy.

## Prerequisites

- A **Virtual Private Server (VPS)** or access to a machine with a public IP address.
- Basic knowledge of server administration and command-line operations.
- A valid **Google API Key**.

## Why Use a Proxy?

In certain regions, direct access to the Google Gemini API may be limited or unavailable. By routing your requests through a proxy server located in a supported country, you can bypass these restrictions and use the API seamlessly.

## Step-by-Step Guide

### 1. Obtain VPS or access to machine with Public IP

You'll need to set up a proxy on a server located in a country where the Google Gemini API is accessible, such as the **United States** or **India**.

#### Recommended VPS Providers

- [DigitalOcean](https://www.digitalocean.com/products/droplets): Offers affordable VPS options starting at `$4` per month.


### 2. Set Up a Proxy Server Using Squid

We recommend using **Squid**, a high-performance proxy caching server for web clients.

#### Install Squid on Your VPS

Follow this comprehensive guide to install and configure Squid:

- **DigitalOcean Squid Installation Guide**: [How To Set Up Squid Proxy on Ubuntu 20.04](https://www.digitalocean.com/community/tutorials/how-to-set-up-squid-proxy-on-ubuntu-20-04)

### 3. Configure Visionatrix to Use the Proxy

After setting up your proxy server, update Visionatrix settings to route API requests through it.

#### Steps to Configure Visionatrix

1. Navigate to the **Settings** page.

2. Input your valid Google API key.

3. Enter your proxy server's connection string.

     **Format Examples:**

     - Without authentication:

       ```
       http://proxy_host:proxy_port
       ```

     - With authentication:

       ```
       http://username:password@proxy_host:proxy_port
       ```

     **Example:**

     - If your proxy's IP is `203.0.113.1` and port is `3128`:

       ```
       http://203.0.113.1:3128
       ```

4. **Save the Settings**

### 4. Alternative: Access the Gemini API Without a Proxy

If you have a payment card connected, you can access the Gemini API directly from almost any country in the world.

#### Steps:

1. Ensure Billing Is Set Up:

    - Log in to your Google Cloud Platform account.
    - Verify that your billing information and credit card are properly connected.

2. Configure Visionatrix:

    - Enter your **Google API Key** in the designated field.
    - Leave the **"Google Proxy"** field empty.

3. Select the Gemini Model:

     - **Gemini Flash**: An affordable option suitable for most users.
     - **Gemini Pro**: Offers superior results but is **not available for free**.
