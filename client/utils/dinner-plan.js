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

function totalPrice(list) {
  const total = (list || []).reduce((sum, item) => {
    if (!item.active) {
      return sum
    }
    return sum + Number(item.price || 0) * Number(item.number || 0)
  }, 0)
  return parseFloat(total.toFixed(2))
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

function buildEatRecordPayload(list, config, remark) {
  const selected = (list || []).filter(item => item.active)
  return {
    user_id: config.fixedUserId,
    person: config.fixedPerson,
    items: selected.map(item => ({
      food_id: item.goodsId,
      food_name: item.name,
      food_image_url: item.pic,
      quantity: item.number,
      price: item.price,
      spec: item.label || ""
    })),
    remark: remark || ""
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
  buildEatRecordPayload,
  buildShopCarInfo,
  mergeShopCarItem,
  noSelect,
  normalizeShopCarInfo,
  removeRecordAfterDelete,
  totalPrice
}
