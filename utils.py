def ema(data, period):
    """
    Menghitung Exponential Moving Average (EMA).
    """
    k = 2 / (period + 1)
    ema_values = []
    for i in range(len(data)):
        if i < period - 1:
            ema_values.append(None)
        elif i == period - 1:
            sma = sum(data[:period]) / period
            ema_values.append(sma)
        else:
            ema_prev = ema_values[i - 1]
            ema_current = data[i] * k + ema_prev * (1 - k)
            ema_values.append(ema_current)
    return ema_values


def rsi(prices, period=14):
    """
    Menghitung Relative Strength Index (RSI).
    """
    if len(prices) < period + 1:
        return [None] * len(prices)

    deltas = [prices[i + 1] - prices[i] for i in range(len(prices) - 1)]
    gains = [max(delta, 0) for delta in deltas]
    losses = [abs(min(delta, 0)) for delta in deltas]

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    rsis = [None] * period
    rs = avg_gain / avg_loss if avg_loss != 0 else float('inf')
    rsis.append(100.0 if avg_loss == 0 else 100 - (100 / (1 + rs)))

    for i in range(period + 1, len(prices)):
        gain = gains[i - 1]
        loss = losses[i - 1]

        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period

        rs = avg_gain / avg_loss if avg_loss != 0 else float('inf')
        rsis.append(100.0 if avg_loss == 0 else 100 - (100 / (1 + rs)))

    while len(rsis) < len(prices):
        rsis.append(None)

    return rsis


def get_signal(ma_short, ma_long, latest_close):
    """
    Menentukan sinyal berdasarkan perbandingan MA dan harga terakhir.
    """
    if ma_short and ma_long:
        if ma_short > ma_long and latest_close > ma_short:
            return "BUY"
        elif ma_short < ma_long and latest_close < ma_short:
            return "SELL"
    return "HOLD"


def trend_strength(ma_short, ma_long):
    """
    Menghitung kekuatan tren dalam persentase.
    """
    if ma_short and ma_long and ma_long != 0:
        return round(abs(ma_short - ma_long) / ma_long * 100, 2)
    return 0.0
