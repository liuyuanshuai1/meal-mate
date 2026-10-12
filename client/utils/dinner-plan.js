function normalizeShopCarInfo(shopCarInfo) {
  return {
    shopNum: shopCarInfo && shopCarInfo.shopNum ? shopCarInfo.shopNum : 0,
    shopList: shopCarInfo && shopCarInfo.shopList ? shopCarInfo.shopList.slice() : []
  }
}

function mergeShopCarItem(shopCarInfo, item) {
  const next = normalizeShopCarInfo(shopCarInfo)
  const incoming = Object.assign({ active: true, left: "", label: "", number: 1 }, item)
  const foundIndex = next.shopList.findIndex(current => (
    current.goodsId == incoming.goodsId &&
    (current.propertyChildIds || "") == (incoming.propertyChildIds || "")
  ))
  if (foundIndex >= 0) {
    const current = next.shopList[foundIndex]
    next.shopList.splice(foundIndex, 1, Object.assign({}, current, incoming, {
      number: Number(current.number || 0) + Number(incoming.number || 0)
    }))
  } else {
    next.shopList.push(incoming)
  }
  next.shopNum = next.shopList.reduce((sum, current) => sum + Number(current.number || 0), 0)
  return next
}

function allSelect(list) {
  return !!(list && list.length) && list.every(item => item.active)
}

function noSelect(list) {
  return !(list || []).some(item => item.active)
}

function buildShopCarInfo(list) {
  const shopList = list || []
  return {
    shopNum: shopList.reduce((sum, item) => sum + Number(item.number || 0), 0),
    shopList
  }
}

function buildDinnerPlanPayload(list) {
  const selected = (list || []).filter(item => item.active)
  return {
    items: selected.map(item => ({
      food_id: item.goodsId,
      quantity: item.number,
      cook_user_id: item.cook_user_id
    }))
  }
}

function buildShoppingList(items) {
  const ingredients = new Map()
  const missingRecipes = []
  ;(items || []).forEach(item => {
    if (!item.recipe_ingredients || !item.recipe_ingredients.length) {
      missingRecipes.push(item.food_name)
      return
    }
    const quantity = Math.max(1, Number(item.quantity || 1))
    item.recipe_ingredients.forEach(ingredient => {
      const name = String(ingredient.name || '').trim()
      if (!name) return
      if (!ingredients.has(name)) ingredients.set(name, { name, amounts: new Map(), notes: new Set() })
      const entry = ingredients.get(name)
      const amount = String(ingredient.amount || '').trim()
      const numeric = amount.match(/^(\d+(?:\.\d+)?)\s*(\D.*)?$/)
      if (numeric) {
        const unit = (numeric[2] || '').trim()
        entry.amounts.set(unit, (entry.amounts.get(unit) || 0) + Number(numeric[1]) * quantity)
      } else {
        entry.notes.add(amount ? amount + (quantity > 1 ? ' ×' + quantity : '') : '按需')
      }
    })
  })
  return {
    items: Array.from(ingredients.values()).map(entry => ({
      name: entry.name,
      amount: [
        ...Array.from(entry.amounts, ([unit, value]) => Number(value.toFixed(2)) + unit),
        ...entry.notes
      ].join(' + ')
    })),
    missingRecipes
  }
}

function formatSchedule(value) {
  if (!value) return '今天吃'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '已预约'
  const pad = number => String(number).padStart(2, '0')
  return (date.getMonth() + 1) + '月' + date.getDate() + '日 ' + pad(date.getHours()) + ':' + pad(date.getMinutes())
}

function appendRecordsPage(existing, pageRecords, reset) {
  return reset ? pageRecords.slice() : (existing || []).concat(pageRecords || [])
}

function removeRecordAfterDelete(records, id, success) {
  if (!success) {
    return records
  }
  return (records || []).filter(record => record.id != id)
}

module.exports = {
  allSelect,
  appendRecordsPage,
  buildDinnerPlanPayload,
  buildShoppingList,
  buildShopCarInfo,
  formatSchedule,
  mergeShopCarItem,
  noSelect,
  normalizeShopCarInfo,
  removeRecordAfterDelete
}
