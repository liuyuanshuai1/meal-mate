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
  buildShopCarInfo,
  mergeShopCarItem,
  noSelect,
  normalizeShopCarInfo,
  removeRecordAfterDelete
}
