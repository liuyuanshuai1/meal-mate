const assert = require('node:assert/strict')
const test = require('node:test')

const {
  allSelect,
  appendRecordsPage,
  buildDinnerPlanPayload,
  buildShoppingList,
  mergeShopCarItem,
  noSelect,
  removeRecordAfterDelete
} = require('../utils/dinner-plan.js')

test('merges same food with same spec and appends different spec', () => {
  const first = mergeShopCarItem({}, {
    goodsId: 1,
    propertyChildIds: 'taste:1',
    name: '番茄炒蛋',
    feeding_value: 18,
    number: 1
  })
  const merged = mergeShopCarItem(first, {
    goodsId: 1,
    propertyChildIds: 'taste:1',
    name: '番茄炒蛋',
    feeding_value: 18,
    number: 2
  })
  const appended = mergeShopCarItem(merged, {
    goodsId: 1,
    propertyChildIds: 'taste:2',
    name: '番茄炒蛋',
    feeding_value: 18,
    number: 1
  })
  assert.equal(appended.shopNum, 4)
  assert.equal(appended.shopList.length, 2)
  assert.equal(appended.shopList[0].number, 3)
})

test('calculates total and selection state', () => {
  const list = [
    { active: true, feeding_value: 18, number: 2 },
    { active: false, feeding_value: 99, number: 1 }
  ]
  assert.equal(allSelect(list), false)
  assert.equal(noSelect(list), false)
  assert.equal(noSelect([{ active: false }]), true)
})

test('builds server-backed dinner plan from selected items only', () => {
  const payload = buildDinnerPlanPayload([
    { active: true, goodsId: 1, name: '番茄炒蛋', pic: 'a.jpg', number: 1, feeding_value: 18, label: '微辣' },
    { active: false, goodsId: 2, name: '米饭', pic: 'b.jpg', number: 1, feeding_value: 2 }
  ])
  assert.equal(payload.items.length, 1)
  assert.equal(payload.items[0].food_id, 1)
  assert.equal(payload.items[0].quantity, 1)
})

test('shopping list combines duplicate ingredients and scales portions', () => {
  const shopping = buildShoppingList([
    { food_name: '番茄炒蛋', quantity: 2, recipe_ingredients: [{ name: '番茄', amount: '2个' }, { name: '鸡蛋', amount: '3个' }] },
    { food_name: '番茄汤', quantity: 1, recipe_ingredients: [{ name: '番茄', amount: '1个' }, { name: '盐', amount: '适量' }] },
    { food_name: '米饭', quantity: 1, recipe_ingredients: [] }
  ])
  assert.deepEqual(shopping.items, [
    { name: '番茄', amount: '5个' },
    { name: '鸡蛋', amount: '6个' },
    { name: '盐', amount: '适量' }
  ])
  assert.deepEqual(shopping.missingRecipes, ['米饭'])
})

test('appends record pages and preserves list on failed delete', () => {
  const first = appendRecordsPage([], [{ id: 1 }], true)
  const second = appendRecordsPage(first, [{ id: 2 }], false)
  assert.deepEqual(second.map(item => item.id), [1, 2])
  assert.deepEqual(removeRecordAfterDelete(second, 1, false).map(item => item.id), [1, 2])
  assert.deepEqual(removeRecordAfterDelete(second, 1, true).map(item => item.id), [2])
})
