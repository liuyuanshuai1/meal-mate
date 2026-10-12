const assert = require('node:assert/strict')
const test = require('node:test')

let pageDefinition
global.Page = definition => { pageDefinition = definition }
global.wx = {
  getStorageSync: () => '',
  setStorage: () => { throw new Error('swipe must not persist the cart') }
}

require('../pages/shop-cart/index.js')

test('updates only the swiped row during touch move', () => {
  const updates = []
  const page = Object.assign({}, pageDefinition, {
    data: {
      delBtnWidth: 120,
      goodsList: { saveHidden: true, list: [{ left: '' }] }
    },
    setData: update => updates.push(update)
  })

  page.touchS({ touches: [{ clientX: 200, clientY: 200 }] })
  page.touchM({
    currentTarget: { dataset: { index: 0 } },
    touches: [{ clientX: 150, clientY: 202 }]
  })

  assert.deepEqual(updates, [{ 'goodsList.list[0].left': 'margin-left:-50px' }])
})

test('vertical swipes leave the cart row alone so the page can scroll', () => {
  const updates = []
  const page = Object.assign({}, pageDefinition, {
    data: { delBtnWidth: 120, goodsList: { list: [{ left: '' }] } },
    setData: update => updates.push(update)
  })
  page.touchS({ touches: [{ clientX: 200, clientY: 200 }] })
  page.touchM({ currentTarget: { dataset: { index: 0 } }, touches: [{ clientX: 196, clientY: 140 }] })
  page.touchE({ currentTarget: { dataset: { index: 0 } }, changedTouches: [{ clientX: 196, clientY: 140 }] })
  assert.deepEqual(updates, [])
})

test('changes the selected dish quantity and saves the new total', () => {
  const saved = []
  const originalSetStorage = wx.setStorage
  wx.setStorage = entry => saved.push(entry.data)
  try {
    const page = Object.assign({}, pageDefinition, {
      data: {
        goodsList: {
          saveHidden: true,
          list: [
            { goodsId: 1, active: true, number: 1, feeding_value: 10 },
            { goodsId: 2, active: true, number: 1, feeding_value: 20 }
          ]
        }
      },
      setData(update) { Object.assign(this.data, update) }
    })

    page.jiaBtnTap({ currentTarget: { dataset: { index: 1 } } })
    assert.deepEqual(page.data.goodsList.list.map(item => item.number), [1, 2])
    assert.equal(saved.at(-1).shopNum, 3)
    assert.equal(page.data.feedingTotal, 50)

    page.jianBtnTap({ currentTarget: { dataset: { index: 1 } } })
    assert.deepEqual(page.data.goodsList.list.map(item => item.number), [1, 1])
    assert.equal(saved.at(-1).shopNum, 2)
  } finally {
    wx.setStorage = originalSetStorage
  }
})
