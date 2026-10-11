const assert = require('node:assert/strict')
const test = require('node:test')

const wxapiPath = require.resolve('../wxapi/main.js')
let requestedText = ''
require.cache[wxapiPath] = {
  id: wxapiPath, filename: wxapiPath, loaded: true,
  exports: {
    recommendFoods: data => {
      requestedText = data.text
      return Promise.resolve({ code: 0, data: { items: [{ food_id: 7, name: '番茄炒蛋', cook_minutes: 15, reason: '正好用上现有食材' }] } })
    }
  }
}

let definition
let navigatedUrl = ''
global.Page = page => { definition = page }
global.wx = {
  showToast: () => {},
  navigateTo: data => { navigatedUrl = data.url }
}

require('../pages/index/index.js')

test('home recommendation sends the request and opens the selected recipe', async () => {
  const page = Object.assign({}, definition, {
    data: Object.assign({}, definition.data, { recommendationText: '  有番茄和鸡蛋  ' }),
    setData(update) { Object.assign(this.data, update) }
  })
  await page.askRecommendation()
  assert.equal(requestedText, '有番茄和鸡蛋')
  assert.equal(page.data.recommendationItems[0].name, '番茄炒蛋')
  assert.equal(page.data.recommendationLoading, false)
  page.toDetailsTap({ currentTarget: { dataset: { id: page.data.recommendationItems[0].food_id } } })
  assert.equal(navigatedUrl, '/pages/goods-details/index?id=7')
})
