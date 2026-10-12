const assert = require('node:assert/strict')
const test = require('node:test')

const planData = {
  id: 9, status: 'pending', notification_unread: true, items: [{
    id: 7, food_id: 4, food_name: '番茄炒蛋', quantity: 1, feeding_value: 10,
    recipe_cook_minutes: 15,
    recipe_ingredients: [{ name: '番茄', amount: '2个' }],
    recipe_steps: ['番茄切块。', '鸡蛋与番茄炒熟。']
  }]
}
let seenPlanId
const wxapiPath = require.resolve('../wxapi/main.js')
require.cache[wxapiPath] = {
  id: wxapiPath, filename: wxapiPath, loaded: true,
  exports: {
    dinnerPlanCurrent: () => Promise.resolve({ code: 0, data: planData }),
    getDinnerPlan: id => Promise.resolve({ code: 0, data: id === 9 ? planData : null }),
    markDinnerPlanSeen: id => { seenPlanId = id; return Promise.resolve({ code: 0 }) }
  }
}

let definition
let navigatedUrl = ''
global.Page = page => { definition = page }
global.wx = {
  showToast: () => {},
  navigateTo: ({ url }) => { navigatedUrl = url }
}

require('../pages/dinner-plan/index.js')
const dinnerPlanPage = definition
require('../pages/shop-cart/index.js')
const cartPage = definition

test('both diners can expand the submitted recipe snapshot', async () => {
  const page = Object.assign({}, dinnerPlanPage, {
    data: Object.assign({}, dinnerPlanPage.data),
    setData(update) { Object.assign(this.data, update) }
  })
  await page.loadPlan()
  assert.equal(page.data.plan.items[0].recipe_steps[1], '鸡蛋与番茄炒熟。')
  page.toggleRecipe({ currentTarget: { dataset: { id: 7 } } })
  assert.equal(page.data.expandedRecipeItemId, 7)
  page.toggleRecipe({ currentTarget: { dataset: { id: 7 } } })
  assert.equal(page.data.expandedRecipeItemId, null)
})

test('cart recipe link opens the dish detail without changing selection', () => {
  cartPage.viewRecipe({ currentTarget: { dataset: { id: 4 } } })
  assert.equal(navigatedUrl, '/pages/goods-details/index?id=4')
})

test('the shopping tab opens the chosen booking and marks the partner reminder read', async () => {
  const page = Object.assign({}, dinnerPlanPage, {
    data: Object.assign({}, dinnerPlanPage.data),
    setData(update) { Object.assign(this.data, update) }
  })
  page.onLoad({ id: '9', tab: 'shopping' })
  await page.loadPlan()
  assert.equal(page.data.activeTab, 'shopping')
  assert.deepEqual(page.data.shoppingList, [{ name: '番茄', amount: '2个' }])
  assert.equal(seenPlanId, 9)
  assert.equal(page.data.plan.notification_unread, false)
})
