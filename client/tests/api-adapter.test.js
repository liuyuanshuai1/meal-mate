const assert = require('node:assert/strict')
const test = require('node:test')

const CONFIG = require('../config.js')
const {
  adaptBannersResponse,
  adaptFoodDetailResponse,
  adaptFoodsResponse,
  adaptRecordsResponse,
  normalizeImageUrl
} = require('../utils/api-adapter.js')

test('adapts food list fields', () => {
  const res = adaptFoodsResponse({
    code: 0,
    data: [{ id: 1, category_id: 2, image_url: 'a.jpg', price: 18, name: '番茄炒蛋' }]
  })
  assert.equal(res.data[0].categoryId, 2)
  assert.equal(res.data[0].pic, 'a.jpg')
  assert.equal(res.data[0].minPrice, 18)
})

test('keeps backend error responses intact', () => {
  const res = adaptFoodsResponse({ code: 500, message: '坏了', data: null })
  assert.equal(res.code, 500)
  assert.equal(res.message, '坏了')
})

test('adapts food detail to page-compatible shape', () => {
  const res = adaptFoodDetailResponse({
    code: 0,
    data: { id: 3, name: '牛肉面', image_url: 'b.jpg', price: 25, description: '热乎' }
  })
  assert.equal(res.data.basicInfo.pic, 'b.jpg')
  assert.equal(res.data.basicInfo.minPrice, 25)
  assert.equal(res.data.pics[0].pic, 'b.jpg')
  assert.equal(res.data.content, '热乎')
  assert.deepEqual(res.data.properties, [])
})

test('adapts banner and record pages', () => {
  const banners = adaptBannersResponse({
    code: 0,
    data: [{ id: 1, image_url: 'banner.jpg', link_type: 'food', food_id: 7 }]
  })
  assert.equal(banners.data[0].picUrl, 'banner.jpg')
  assert.equal(banners.data[0].businessId, 7)

  const records = adaptRecordsResponse({
    code: 0,
    data: { items: [{ id: 1, total_price: 18, items: [{ food_name: '番茄炒蛋' }] }], total: 1 }
  })
  assert.equal(records.data.records.length, 1)
  assert.equal(records.data.records[0].items[0].food_name, '番茄炒蛋')
})

test('normalizes backend static image paths', () => {
  const apiOrigin = CONFIG.apiBaseUrl.replace(/\/api\/?$/, '')

  assert.equal(
    normalizeImageUrl('/static/uploads/小白和小黄2.jpg'),
    `${apiOrigin}/static/uploads/小白和小黄2.jpg`
  )

  const banners = adaptBannersResponse({
    code: 0,
    data: [{ id: 1, image_url: '/static/uploads/banner.jpg' }]
  })
  assert.equal(banners.data[0].picUrl, `${apiOrigin}/static/uploads/banner.jpg`)
})
