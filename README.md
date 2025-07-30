# Gamma-Aware Delta Hedging Bot

Hello! Welcome to your new automated hedging bot. Think of this bot as a smart assistant that helps protect your cryptocurrency investment on Uniswap v3.

## What Does This Bot Do?

Imagine you're providing liquidity to a pool on Uniswap v3. This is a bit like running a small currency exchange office. As the price of the crypto you're providing changes, the value of your investment can go up or down. This bot automatically watches the market and makes small trades on another platform (Hyperliquid) to counteract, or "hedge," the price risk, helping to keep your investment more stable. It's like having an umbrella ready for a rainy day!

## What You Need Before You Start

1.  **Docker:** A program that lets us run our bot in its own special, clean environment. You can download it from the official Docker website.
2.  **A Google Account:** We'll use Google Sheets to create a control panel for the bot.
3.  **An n8n Account:** n8n is the "brain" that will run our bot on a schedule. You can use their cloud service or run it locally.
4.  **A Hyperliquid Account:** This is where the bot will make its hedging trades. You will need to create a main account and then a special, separate **sub-account** just for the bot.

---

## Step-by-Step Setup Guide

Follow these steps carefully, and your bot will be up and running in no time!

### Part 1: Get the Bot's Environment Ready (Docker)

This step builds the "house" where our bot will live.

1.  **Open Your Computer's Terminal:** This is an application that lets you type commands. On Mac, it's called Terminal. On Windows, it's called Command Prompt or PowerShell.
2.  **Navigate to the Folder:** Use the `cd` command to go into the `Nabla V3.2` folder where this README file is.
3.  **Build the Docker Image:** Copy and paste the following command into your terminal and press Enter. This reads the `Dockerfile` and builds the bot's environment.
    ```shell
    docker build -t n8n-hedger-image .
    ```
    (Don't forget the period `.` at the end!)

### Part 2: Build the Bot's Control Panel (Google Sheets)

This is where you'll tell the bot what to do and see what it has done.

1.  **Create a New Google Sheet.**
2.  **Create the `Configuration` Tab:**
    *   Rename the first sheet (tab at the bottom) to `Configuration`.
    *   In the very first row, create these column headers: `asset_pair`, `initial_liquidity_L`, `price_lower_Pa`, `price_upper_Pb`, `hedge_asset`, `deadband_type`, `risk_parameter_C`, `max_leverage`.
    *   In the second row, fill in your strategy details. For example: `ETH/USDC`, `10000`, `2000`, `2500`, `ETH`, `absolute`, `0.1`, `5`.

> **Important Note on Strategies:**
> The current design is built to run **one single strategy**. The bot reads the headers from Row 1 and the configuration for your single strategy from **Row 2**.
>
> If you want to run multiple strategies (e.g., one on Row 2, another on Row 3, etc.), you would need to modify the n8n workflow to loop through each row after the header. The current setup does not do this automatically.
3.  **Create the `Persistent Log` Tab:**
    *   Click the `+` button to add a new sheet.
    *   Rename this new sheet to `Persistent Log`.
    *   In the first row, create these headers: `Timestamp`, `ExecutionID`, `Action`, `LP_Delta`, `Hedge_Size_Required`, `Trade_Size_Executed`, `Fill_Price`, `Cloid`, `Message`.

### Understanding Your Control Panel

Here’s what all the columns in your Google Sheets mean.

#### Configuration Tab Parameters

This sheet is where you give the bot its instructions.

*   **`asset_pair`**: The specific Uniswap v3 liquidity pool you are in (e.g., `ETH/USDC`).
*   **`initial_liquidity_L`**: The "L" value from your Uniswap v3 position. This is a specific number from the Uniswap interface that represents the size of your position.
*   **`price_lower_Pa`**: The bottom price of your Uniswap v3 position's active range.
*   **`price_upper_Pb`**: The top price of your Uniswap v3 position's active range.
*   **`hedge_asset`**: The cryptocurrency the bot will trade on Hyperliquid to protect your position (e.g., `ETH`). This should usually be the volatile asset in your pair.
*   **`deadband_type`**: The method for deciding when a trade is necessary. For now, just use `absolute`.
*   **`risk_parameter_C`**: This is the size of the "deadband" or "do-nothing zone," denominated in your `hedge_asset`. If the required hedge trade is smaller than this number, the bot will wait. This prevents lots of tiny, costly trades.
        > **How to Calculate It:** A good starting value is 5-10% of your total position size, converted into the `hedge_asset`.
        > **Example:** If your LP position is worth $10,000 and your `hedge_asset` (ETH) is priced at $2,500, your position size is 4 ETH. A 10% deadband would be **`0.4`**.
*   **`max_leverage`**: The maximum leverage the bot is allowed to use for its hedge trades on Hyperliquid. **Start with a low number like `1` or `2` for safety.**

#### Persistent Log Tab Parameters

This sheet is the bot's diary. It writes down everything it does so you can check its work.

*   **`Timestamp`**: The exact date and time the action happened.
*   **`ExecutionID`**: The unique ID n8n gives to that specific run of the workflow.
*   **`Action`**: A short description of what the bot did (e.g., `CALCULATE_DELTA`, `EXECUTE_TRADE`, `ERROR`).
*   **`LP_Delta`**: The calculated risk ("delta") of your LP position at that moment.
*   **`Hedge_Size_Required`**: The size of the trade the bot calculated it needed to make.
*   **`Trade_Size_Executed`**: The actual size of the trade the bot successfully made.
*   **`Fill_Price`**: The average price at which the hedge trade was executed.
*   **`Cloid`**: The unique "Client Order ID" for the trade order sent to Hyperliquid. This helps prevent duplicate trades.
*   **`Message`**: Any important information, like a success message or the specific details of an error if something went wrong.
### Getting Started: A Safe Example

Feeling overwhelmed by the parameters? Here is a safe, conservative example setup for a user providing $2,000 of liquidity to an ETH/USDC pool. You can use this as a template.

**Assumptions:**
*   Total LP Position Value: $2,000
*   Current ETH Price: $2,500
*   Your Uniswap v3 Range: $2,200 to $2,800

Copy these values into the second row of your `Configuration` sheet:

| asset_pair | initial_liquidity_L | price_lower_Pa | price_upper_Pb | hedge_asset | deadband_type | risk_parameter_C | max_leverage |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `ETH/USDC` | `(Your L value from Uniswap)` | `2200` | `2800` | `ETH` | `absolute` | `0.08` | `2` |

**Why these values are safe:**
*   **`max_leverage` = 2**: This is low and reduces the risk of liquidation on your hedge.
*   **`risk_parameter_C` = 0.08**: Your position is worth 0.8 ETH ($2000 / $2500). This sets a 10% deadband (0.8 * 0.10), which is a reasonable starting point to avoid excessive trading.

---

### Part 3: Set Up the Bot's Brain (n8n)

This connects everything and tells the bot when to wake up and check things.

1.  **Create a New Workflow in n8n.**
2.  **Follow the instructions** provided in the project documentation to add and connect all the nodes (Schedule, Google Sheets, Execute Command, etc.). This will build the logic that:
    *   Wakes up every minute.
    *   Reads your settings from the `Configuration` sheet.
    *   Calculates if a trade is needed.
    *   Executes the trade if necessary.
    *   Writes a log of what it did in the `Persistent Log` sheet.

### Part 4: Test Everything Safely! (Testnet)

Before using real money, we'll do a practice run.

1.  **Edit the `trade_executor.py` file** located in the `scripts` folder.
2.  **Find the lines** that say `constants.MAINNET_API_URL`.
3.  **Change them** to point to the testnet URL: `"https://api.hyperliquid-testnet.xyz"`. This is like telling the bot to use play money instead of real money.
4.  **Run your n8n workflow.** Watch the `Persistent Log` sheet to make sure it's working correctly.

### Part 5: Go Live! (Mainnet)

Once you're sure everything works, it's time to go live.

1.  **Create a Sub-Account:** In Hyperliquid, create a new, empty sub-account. **This is very important for safety!** Only put the money you want the bot to use in this sub-account.
2.  **Get Your API Keys:** Get the API secret (private key) and address for this **new sub-account**.
3.  **Update the Script:** Change the URL in `trade_executor.py` back to `constants.MAINNET_API_URL`.
4.  **Run the Bot:** Use the final `docker run` command from the project documentation. Make sure to replace the placeholder text with your real sub-account API keys and the correct file path to the `scripts` folder.

    ```shell
    # Example command - replace with your real info!
    docker run -it --rm --name n8n-hedger \
      -p 5678:5678 \
      -v /path/to/your/Nabla V3.2/scripts:/scripts \
      -e HYPERLIQUID_API_SECRET="0xYourSubAccountPrivateKey" \
      -e HYPERLIQUID_ADDRESS="YourSubAccountAddress" \
      n8n-hedger-image
    ```

## How It Works: The Simple Version

1.  **Check Time:** The n8n workflow starts on a schedule (e.g., every minute).
2.  **Read Settings:** It reads your strategy settings from the Google Sheet.
3.  **Calculate Risk:** It runs the `state_calculator.py` script to figure out its current risk (the "delta").
4.  **Decide:** It decides if the risk is large enough to need a hedge trade.
5.  **Trade (If Needed):** If a trade is needed, it runs the `trade_executor.py` script to make the trade on Hyperliquid.
6.  **Log:** It writes down everything it did in the `Persistent Log` sheet so you can see its work.

## SAFETY FIRST!

*   **Start Small:** When you go live, start with a very small amount of money.
*   **Use a Sub-Account:** Never run this bot with your main account's API keys. Always use a dedicated, separate sub-account.
*   **Test Thoroughly:** Make sure you understand how it works on the testnet before even thinking about using real funds.
*   **Monitor:** Keep an eye on the `Persistent Log` sheet to make sure the bot is behaving as you expect.

Good luck!