const assert = require('node:assert/strict')
const test = require('node:test')

const wxapiPath = require.resolve('../wxapi/main.js')
let requestedText = ''
let exploredText = ''
require.cache[wxapiPath] = {
  id: wxapiPath, filename: wxapiPath, loaded: true,
  exports: {
    banners: () => Promise.resolve({ code: 0, data: [] }),
    dinnerPlansUpcoming: () => Promise.resolve({ code: 0, data: [{
      id: 23, creator_name: '小明', notification_unread: true,
      scheduled_for: '2026-10-16T18:00:00+08:00', items: [{ id: 1 }], feeding_total: 12
    }] }),
    recommendFoods: data => {
      requestedText = data.text
      return Promise.resolve({ code: 0, data: { items: [{ food_id: 7, name: '番茄炒蛋', cook_minutes: 15, reason: '正好用上现有食材' }] } })
    },
    exploreRecipes: data => {
      exploredText = data.text
      return Promise.resolve({ code: 0, data: { items: [{
        name: '青椒鸡蛋饼', cook_minutes: 15, servings: 2, reason: '用上现有食材',
        ingredients: [{ name: '青椒', amount: '1个' }],
        missing_ingredients: ['面粉'], steps: ['切碎青椒', '拌面糊煎熟']
      }] } })
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

test('exploration shows a generated recipe inline without navigating to a menu food', async () => {
  const page = Object.assign({}, definition, {
    data: Object.assign({}, definition.data, { recommendationText: '  有青椒和鸡蛋  ' }),
    setData(update) { Object.assign(this.data, update) }
  })
  page.switchRecommendationMode({ currentTarget: { dataset: { mode: 'explore' } } })
  await page.askRecommendation()
  assert.equal(exploredText, '有青椒和鸡蛋')
  assert.equal(page.data.explorationItems[0].missing_text, '面粉')
  assert.equal(page.data.recommendationItems.length, 0)
  page.toggleExplorationItem({ currentTarget: { dataset: { index: 0 } } })
  assert.equal(page.data.expandedExplorationIndex, 0)
  page.toggleExplorationItem({ currentTarget: { dataset: { index: 0 } } })
  assert.equal(page.data.expandedExplorationIndex, -1)
})

test('home shows the shared booking and opens its shopping list', async () => {
  const page = Object.assign({}, definition, {
    data: Object.assign({}, definition.data),
    setData(update) { Object.assign(this.data, update) }
  })
  page.loadHome()
  await Promise.resolve()
  assert.equal(page.data.upcomingPlans[0].notification_unread, true)
  assert.match(page.data.upcomingPlans[0].schedule_text, /10月16日/)
  page.goSharedPlan({ currentTarget: { dataset: { id: 23, tab: 'shopping' } } })
  assert.equal(navigatedUrl, '/pages/dinner-plan/index?id=23&tab=shopping')
})
