const CONFIG = require('../config.js')

function getApiOrigin() {
  return CONFIG.apiBaseUrl.replace(/\/api\/?$/, '')
}

function normalizeImageUrl(url) {
  if (!url || typeof url !== 'string') {
    return url || ""
  }
  if (/^(https?:)?\/\//.test(url) || url.indexOf('data:') === 0 || url.indexOf('wxfile:') === 0) {
    return url
  }
  if (url.charAt(0) === '/') {
    return getApiOrigin() + url
  }
  return url
}

function pickArray(data) {
  if (Array.isArray(data)) {
    return data
  }
  if (!data) {
    return []
  }
  return data.items || data.list || data.result || data.records || []
}

function adaptFood(food) {
  if (!food) {
    return food
  }
  return Object.assign({}, food, {
    categoryId: food.categoryId || food.category_id,
    pic: normalizeImageUrl(food.pic || food.image_url || ""),
    minPrice: food.minPrice !== undefined ? food.minPrice : food.price
  })
}

function adaptFoodsResponse(res) {
  if (!res || res.code !== 0) {
    return res
  }
  return Object.assign({}, res, {
    data: pickArray(res.data).map(adaptFood)
  })
}

function adaptFoodDetailResponse(res) {
  if (!res || res.code !== 0) {
    return res
  }
  const food = res.data || {}
  const adapted = adaptFood(food.basicInfo ? food.basicInfo : food)
  const pics = food.pics && food.pics.length ? food.pics : [{ pic: adapted.pic }]
  return Object.assign({}, res, {
    data: Object.assign({}, food, {
      basicInfo: Object.assign({ stores: 999 }, adapted),
      pics: pics.map(item => ({ pic: normalizeImageUrl(item.pic || item.image_url || adapted.pic) })),
      content: food.content || food.description || "",
      properties: food.properties || []
    })
  })
}

function adaptBannersResponse(res) {
  if (!res || res.code !== 0) {
    return res
  }
  return Object.assign({}, res, {
    data: pickArray(res.data).map(item => Object.assign({}, item, {
      picUrl: normalizeImageUrl(item.picUrl || item.image_url || item.pic || ""),
      businessId: item.businessId || item.food_id || item.link_id || 0
    }))
  })
}

function adaptRecordsResponse(res) {
  if (!res || res.code !== 0) {
    return res
  }
  const data = res.data || {}
  const records = pickArray(data).map(record => Object.assign({}, record, {
    items: record.items || []
  }))
  return Object.assign({}, res, {
    data: {
      records,
      total: data.total || records.length
    }
  })
}

module.exports = {
  adaptBannersResponse,
  adaptFood,
  adaptFoodsResponse,
  adaptFoodDetailResponse,
  adaptRecordsResponse,
  normalizeImageUrl,
  pickArray
}
