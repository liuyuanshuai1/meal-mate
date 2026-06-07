const CONFIG = require('../config.js')
const {
  adaptBannersResponse,
  adaptFoodDetailResponse,
  adaptFoodsResponse,
  adaptRecordsResponse
} = require('../utils/api-adapter.js')

const request = (url, method, data) => {
  return new Promise((resolve, reject) => {
    wx.request({
      url: CONFIG.apiBaseUrl + url,
      method: method.toUpperCase(),
      data: data || {},
      header: {
        'Content-Type': 'application/json'
      },
      success(result) {
        resolve(result.data)
      },
      fail(error) {
        reject(error)
      }
    })
  })
}

Promise.prototype.finally = function (callback) {
  var Promise = this.constructor
  return this.then(
    function (value) {
      return Promise.resolve(callback()).then(function () {
        return value
      })
    },
    function (reason) {
      return Promise.resolve(callback()).then(function () {
        throw reason
      })
    }
  )
}

function withMessage(promise) {
  return promise.then(res => {
    if (res && res.code !== 0 && res.message) {
      wx.showToast({
        title: res.message,
        icon: 'none'
      })
    }
    return res
  })
}

module.exports = {
  request,
  banners: (data) => withMessage(request('/banners', 'get', data).then(adaptBannersResponse)),
  foodCategories: (data) => withMessage(request('/food-categories', 'get', data)),
  foods: (data) => withMessage(request('/foods', 'get', data).then(adaptFoodsResponse)),
  foodDetail: (id) => withMessage(request('/foods/' + id, 'get').then(adaptFoodDetailResponse)),
  createEatRecord: (data) => withMessage(request('/eat-records', 'post', data)),
  eatRecords: (data) => withMessage(request('/eat-records', 'get', data).then(adaptRecordsResponse)),
  deleteEatRecord: (id) => withMessage(request('/eat-records/' + id + '?user_id=' + CONFIG.fixedUserId, 'delete')),

  goodsCategory: (data) => withMessage(request('/food-categories', 'get', data)),
  goods: (data) => withMessage(request('/foods', 'get', data).then(adaptFoodsResponse)),
  goodsDetail: (id) => withMessage(request('/foods/' + id, 'get').then(adaptFoodDetailResponse)),
  goodsPrice: (data) => Promise.resolve({
    code: 0,
    data: {
      price: data.price || 0,
      stores: 999
    },
    message: ""
  }),
  queryConfigBatch: () => Promise.resolve({
    code: 0,
    data: [{ key: 'mallName', value: '一起吃饭叭' }],
    message: ""
  }),
  checkToken: () => Promise.resolve({ code: 0, data: {}, message: "" }),

  queryMobileLocation: (data) => request('/common/mobile-segment/location', 'get', data),
  queryConfig: (data) => request('/config/get-value', 'get', data),
  scoreRules: (data) => request('/score/send/rule', 'post', data),
  scoreSign: (token) => request('/score/sign', 'post', { token }),
  scoreSignLogs: (data) => request('/score/sign/logs', 'post', data),
  scoreTodaySignedInfo: (token) => request('/score/today-signed', 'get', { token }),
  scoreExchange: (number, token) => request('/score/exchange', 'post', { number, token }),
  scoreLogs: (data) => request('/score/logs', 'post', data),
  kanjiaList: () => Promise.resolve({ code: 0, data: { result: [], goodsMap: {} }, message: "" }),
  kanjiaSet: () => Promise.resolve({ code: 404, data: {}, message: "" }),
  kanjiaJoin: (kjid, token) => request('/shop/goods/kanjia/join', 'post', { kjid, token }),
  kanjiaDetail: (kjid, joiner) => request('/shop/goods/kanjia/info', 'get', { kjid, joiner }),
  kanjiaHelp: (kjid, joiner, token, remark) => request('/shop/goods/kanjia/help', 'post', {
    kjid,
    joinerUser: joiner,
    token,
    remark
  }),
  kanjiaHelpDetail: (kjid, joiner, token) => request('/shop/goods/kanjia/myHelp', 'get', {
    kjid,
    joinerUser: joiner,
    token
  }),
  addTempleMsgFormid: (data) => request('/template-msg/wxa/formId', 'post', data),
  sendTempleMsg: (data) => request('/template-msg/put', 'post', data),
  wxpay: (data) => request('/pay/wx/wxapp', 'post', data),
  alipay: (data) => request('/pay/alipay/semiAutomatic/payurl', 'post', data),
  login: (code) => request('/user/wxapp/login', 'post', { code, type: 2 }),
  register: (data) => request('/user/wxapp/register/complex', 'post', data),
  coupons: () => Promise.resolve({ code: 0, data: [], message: "" }),
  couponDetail: (id) => request('/discounts/detail', 'get', { id }),
  myCoupons: (data) => request('/discounts/my', 'get', data),
  fetchCoupons: (data) => request('/discounts/fetch', 'post', data),
  noticeList: (data) => request('/notice/list', 'post', data),
  noticeDetail: (id) => request('/notice/detail', 'get', { id }),
  addAddress: (data) => request('/user/shipping-address/add', 'post', data),
  updateAddress: (data) => request('/user/shipping-address/update', 'post', data),
  deleteAddress: (id, token) => request('/user/shipping-address/delete', 'post', { id, token }),
  queryAddress: (token) => request('/user/shipping-address/list', 'get', { token }),
  defaultAddress: (token) => request('/user/shipping-address/default', 'get', { token }),
  addressDetail: (id, token) => request('/user/shipping-address/detail', 'get', { id, token }),
  pingtuanSet: () => Promise.resolve({ code: 404, data: {}, message: "" }),
  pingtuanOpen: (goodsId, token) => request('/shop/goods/pingtuan/open', 'post', { goodsId, token }),
  pingtuanList: () => Promise.resolve({ code: 0, data: [], message: "" }),
  videoDetail: (videoId) => request('/media/video/detail', 'get', { videoId }),
  bindMobile: (data) => request('/user/wxapp/bindMobile', 'post', data),
  userDetail: (token) => request('/user/detail', 'get', { token }),
  userAmount: () => Promise.resolve({ code: 0, data: { balance: 0, freeze: 0, score: 0 }, message: "" }),
  orderCreate: (data) => request('/order/create', 'post', data),
  orderList: () => Promise.resolve({ code: 0, data: { orderList: [], logisticsMap: {}, goodsMap: {} }, message: "" }),
  orderDetail: (id, token) => request('/order/detail', 'get', { id, token }),
  orderDelivery: (orderId, token) => request('/order/delivery', 'post', { orderId, token }),
  orderReputation: (data) => request('/order/reputation', 'post', data),
  orderClose: (orderId, token) => request('/order/close', 'post', { orderId, token }),
  orderPay: (orderId, token) => request('/order/pay', 'post', { orderId, token }),
  orderStatistics: (token) => request('/order/statistics', 'get', { token }),
  withDrawApply: (money, token) => request('/user/withDraw/apply', 'post', { money, token }),
  province: () => request('/common/region/v2/province', 'get'),
  nextRegion: (pid) => request('/common/region/v2/child', 'get', { pid }),
  cashLogs: (data) => request('/user/cashLog', 'post', data),
  rechargeSendRules: () => request('/user/recharge/send/rule', 'get'),
  payBillDiscounts: () => request('/payBill/discounts', 'get'),
  payBill: (data) => request('/payBill/pay', 'post', data),
  vipLevel: () => request('/config/vipLevel', 'get'),
  fxApply: (token, name, mobile) => request('/saleDistribution/apply', 'post', { token, name, mobile }),
  fxApplyProgress: (token) => request('/saleDistribution/apply/progress', 'get', { token }),
  fxMembers: (data) => request('/saleDistribution/members', 'post', data),
  fxCommisionLog: (data) => request('/saleDistribution/commision/log', 'post', data),
  wxaQrcode: (data) => request('/qrcode/wxa/unlimit', 'post', data),
  shopSubList: () => Promise.resolve({ code: 0, data: [], message: "" }),
  shopSubdetail: (id) => request('/shop/subshop/detail/v2', 'get', { id })
}
