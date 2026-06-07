const assert = require('node:assert/strict')
const test = require('node:test')

const {
  allSelect,
  appendRecordsPage,
  buildEatRecordPayload,
  mergeShopCarItem,
  noSelect,
  removeRecordAfterDelete,
  totalPrice
} = require('../utils/dinner-plan.js')

test('merges same food with same spec and appends different spec', () => {
  const first = mergeShopCarItem({}, {
    goodsId: 1,
    propertyChildIds: 'taste:1',
    name: '番茄炒蛋',
    price: 18,
    number: 1
  })
  const merged = mergeShopCarItem(first, {
    goodsId: 1,
    propertyChildIds: 'taste:1',
    name: '番茄炒蛋',
    price: 18,
    number: 2
  })
  const appended = mergeShopCarItem(merged, {
    goodsId: 1,
    propertyChildIds: 'taste:2',
    name: '番茄炒蛋',
    price: 18,
    number: 1
  })
  assert.equal(appended.shopNum, 4)
  assert.equal(appended.shopList.length, 2)
  assert.equal(appended.shopList[0].number, 3)
})

test('calculates total and selection state', () => {
  const list = [
    { active: true, price: 18, number: 2 },
    { active: false, price: 99, number: 1 }
  ]
  assert.equal(totalPrice(list), 36)
  assert.equal(allSelect(list), false)
  assert.equal(noSelect(list), false)
  assert.equal(noSelect([{ active: false }]), true)
})

test('builds eat record payload from selected items only', () => {
  const payload = buildEatRecordPayload([
    { active: true, goodsId: 1, name: '番茄炒蛋', pic: 'a.jpg', number: 1, price: 18, label: '微辣' },
    { active: false, goodsId: 2, name: '米饭', pic: 'b.jpg', number: 1, price: 2 }
  ], {
    fixedUserId: 1,
    fixedPerson: 'default'
  }, '')
  assert.equal(payload.user_id, 1)
  assert.equal(payload.items.length, 1)
  assert.equal(payload.items[0].food_id, 1)
  assert.equal(payload.items[0].spec, '微辣')
})

test('appends record pages and preserves list on failed delete', () => {
  const first = appendRecordsPage([], [{ id: 1 }], true)
  const second = appendRecordsPage(first, [{ id: 2 }], false)
  assert.deepEqual(second.map(item => item.id), [1, 2])
  assert.deepEqual(removeRecordAfterDelete(second, 1, false).map(item => item.id), [1, 2])
  assert.deepEqual(removeRecordAfterDelete(second, 1, true).map(item => item.id), [2])
})
