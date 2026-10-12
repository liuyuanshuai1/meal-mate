const assert = require('node:assert/strict')
const test = require('node:test')

const wxapiPath = require.resolve('../wxapi/main.js')
let submittedPayload
require.cache[wxapiPath] = {
  id: wxapiPath, filename: wxapiPath, loaded: true,
  exports: {
    diningGroupCurrent: () => Promise.resolve({ code: 0, data: { id: 1, members: [{ user_id: 1 }, { user_id: 2 }] } }),
    createDinnerPlan: payload => {
      submittedPayload = payload
      return Promise.resolve({ code: 0, data: { id: 17 } })
    }
  }
}

let definition
let navigatedUrl
global.Page = page => { definition = page }
global.wx = {
  showLoading: () => {}, hideLoading: () => {}, showToast: () => {},
  removeStorageSync: () => {},
  navigateTo: ({ url }) => { navigatedUrl = url }
}
require('../pages/shop-cart/index.js')

test('reserving selected dishes sends an ISO time and opens that booking', async () => {
  const date = new Date(Date.now() + 3 * 24 * 60 * 60 * 1000)
  const pad = value => String(value).padStart(2, '0')
  const reservationDate = date.getFullYear() + '-' + pad(date.getMonth() + 1) + '-' + pad(date.getDate())
  const page = Object.assign({}, definition, {
    data: Object.assign({}, definition.data, {
      members: [{ user_id: 1 }, { user_id: 2 }],
      reservationEnabled: true, reservationDate, reservationTime: '18:00',
      goodsList: { list: [{ active: true, goodsId: 5, number: 2, cook_user_id: 1 }] }
    }),
    setData(update) { Object.assign(this.data, update) }
  })
  await page.toPayOrder()
  assert.equal(submittedPayload.items[0].quantity, 2)
  assert.equal(new Date(submittedPayload.scheduled_for).getTime(), new Date(reservationDate + 'T18:00:00').getTime())
  assert.equal(navigatedUrl, '/pages/dinner-plan/index?id=17')
})
