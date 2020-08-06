import futu as ft
import constants
import math


class TradeManager():
    trade_hk_ctx = None

    def unlock_trade_password(self, host, port, password, connect):
        trade_hk_ctx = ft.OpenFutureTradeContext(host, port)
        ret_code, error_message = trade_hk_ctx.unlock_trade(password=password)
        if connect is False or ret_code == ft.RET_ERROR:
            trade_hk_ctx.close()
        else:
            self.trade_hk_ctx = trade_hk_ctx
        if ret_code == ft.RET_ERROR:
            return False, "交易密碼不正確，請確保輸入無誤以免帳戶被暫時鎖定"
        else:
            return True, "交易密碼正確"

    def disconnect(self):
        try:
            if self.trade_hk_ctx is not None:
                self.trade_hk_ctx.close()
                self.trade_hk_ctx = None
        except:
            pass

    def get_holding_position_and_quantity(self, product_code_month, trade_product_hsi, trade_product_mhi):
        ret_code, ret_data = self.trade_hk_ctx.position_list_query()
        total_row = ret_data.shape[0]
        hsi_position_on_hand = None
        mhi_position_on_hand = None
        hsi_quantity_on_hand = 0
        mhi_quantity_on_hand = 0
        for i in range(total_row):
            position_side = ret_data['position_side'][i]
            position_code = str(ret_data['code'][i])
            qty = abs(int(ret_data['qty'][i]))
            if qty > 0:
                if trade_product_hsi is True and position_code.endswith(
                        f'{constants.TradeProductCode.HSI}{product_code_month}'):
                    hsi_quantity_on_hand += qty
                    hsi_position_on_hand = constants.TradeDirection.SELL if position_side == ft.PositionSide.SHORT \
                        else constants.TradeDirection.BUY
                elif trade_product_mhi is True and position_code.endswith(
                        f'{constants.TradeProductCode.MHI}{product_code_month}'):
                    mhi_quantity_on_hand = mhi_quantity_on_hand + qty
                    mhi_position_on_hand = constants.TradeDirection.SELL if position_side == ft.PositionSide.SHORT \
                        else constants.TradeDirection.BUY
        return hsi_position_on_hand, hsi_quantity_on_hand, mhi_position_on_hand, mhi_quantity_on_hand

    def get_available_funds(self):
        ret_code, ret_data = self.trade_hk_ctx.accinfo_query(trd_env=ft.TrdEnv.REAL)
        available_funds = round(ret_data['available_funds'][0], 2)
        return available_funds

    def get_max_trade_quantity(self, hsi_margin, mhi_margin, trade_product_hsi, trade_product_mhi):
        available_funds = self.get_available_funds()
        hsi_quantity = 0
        mhi_quantity = 0
        if trade_product_hsi is True:
            hsi_quantity = math.floor(available_funds / hsi_margin)
        if trade_product_mhi is True:
            mhi_quantity = math.floor((available_funds - hsi_margin * hsi_quantity) / mhi_margin)
        return hsi_quantity, mhi_quantity

    def place_order(self, product_code_prefix, product_code_month, direction, price, quantity):
        trade_code = f"HK.{product_code_prefix}{product_code_month}"
        if direction == constants.TradeDirection.BUY:
            trade_side = ft.TrdSide.BUY
        else:
            trade_side = ft.TrdSide.SELL
        ret_code, ret_data = self.trade_hk_ctx.place_order(price=price, qty=quantity, code=trade_code,
                                                           trd_side=trade_side,
                                                           trd_env=ft.TrdEnv.REAL)
        if ret_code == ft.RET_OK:
            return True, ret_data.iloc[0], None
        else:
            return False, None, ret_data

    def get_order_list_by_order_id_list(self, order_id_list):
        if len(order_id_list) == 1:
            ret_code, ret_data = self.trade_hk_ctx.order_list_query(order_id=order_id_list[0], trd_env=ft.TrdEnv.REAL)
        else:
            ret_code, ret_data = self.trade_hk_ctx.order_list_query(trd_env=ft.TrdEnv.REAL)
        total_row = ret_data.shape[0]
        order_status_list = []
        for i in range(total_row):
            order_id = ret_data['order_id'][i]
            if order_id in order_id_list:
                order_status_list.append({
                    'order_id': order_id,
                    'code': ret_data['code'][i],
                    'order_status': ret_data['order_status'][i],
                    'price': ret_data['price'][i],
                    'qty': ret_data['qty'][i],
                    'dealt_qty': ret_data['dealt_qty'][i],
                    'dealt_avg_price': ret_data['dealt_avg_price'][i]
                })
        return order_status_list

    def cancel_order(self, order_data):
        self.trade_hk_ctx.modify_order(order_id=order_data['order_id'], modify_order_op=ft.ModifyOrderOp.CANCEL,
                                       price=order_data['price'], qty=order_data['qty'], trd_env=ft.TrdEnv.REAL)

    def modify_order(self, order_id, price, qty):
        self.trade_hk_ctx.modify_order(modify_order_op=ft.ModifyOrderOp.NORMAL, order_id=order_id,
                                       trd_env=ft.TrdEnv.REAL, price=price, qty=qty)
