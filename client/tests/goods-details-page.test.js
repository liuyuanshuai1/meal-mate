const assert = require('node:assert/strict')
const test = require('node:test')

const wxParsePath = require.resolve('../wxParse/wxParse.js')
require.cache[wxParsePath] = { id: wxParsePath, filename: wxParsePath, loaded: true, exports: {} }

let pageDefinition
let storedCart = {}
let writes = 0
global.Page = definition => { pageDefinition = definition }
global.getCurrentPages = () => []
global.wx = {
  getStorageSync: () => storedCart,
  setStorageSync: (key, value) => { storedCart = value; writes++ },
  showToast: () => {},
  switchTab: () => {}
}

require('../pages/goods-details/index.js')

test('one add tap stores one portion and ignores a second tap during navigation', () => {
  storedCart = {}
  writes = 0
  const page = Object.assign({}, pageDefinition, {
    data: Object.assign({}, pageDefinition.data, {
      goodsDetail: { basicInfo: { id: 7, name: '番茄炒蛋', feeding_value: 18 }, properties: [] },
      buyNumber: 1
    }),
    setData(update) { Object.assign(this.data, update) }
  })

  page.addShopCar()
  page.addShopCar()

  assert.equal(writes, 1)
  assert.equal(storedCart.shopNum, 1)
  assert.equal(storedCart.shopList[0].number, 1)
})
