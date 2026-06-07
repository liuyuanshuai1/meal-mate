const WXAPI = require('../../wxapi/main')
const CONFIG = require('../../config.js')

Page({
  data: {
    swiperCurrent: 0,
    bannerList: [],
    goodsRecommend: [],
    recentFoods: []
  },
  onLoad: function() {
    wx.setNavigationBarTitle({
      title: '一起吃饭叭'
    })
  },
  onShow() {
    this.loadHome()
  },
  loadHome() {
    WXAPI.banners().then(res => {
      if (res.code === 0) {
        this.setData({
          bannerList: res.data || []
        })
      }
    })
    WXAPI.foods({
      recommended: true,
      page: 1,
      page_size: 20
    }).then(res => {
      if (res.code === 0) {
        this.setData({
          goodsRecommend: res.data || []
        })
      }
    })
    WXAPI.eatRecords({
      user_id: CONFIG.fixedUserId,
      page: 1,
      page_size: 3
    }).then(res => {
      if (res.code === 0) {
        const recentFoods = []
        ;(res.data.records || []).forEach(record => {
          ;(record.items || []).forEach(item => {
            if (recentFoods.length < 6) {
              recentFoods.push(item.food_name || item.name)
            }
          })
        })
        this.setData({ recentFoods })
      }
    })
  },
  swiperchange: function(e) {
    this.setData({
      swiperCurrent: e.detail.current
    })
  },
  toDetailsTap: function(e) {
    wx.navigateTo({
      url: "/pages/goods-details/index?id=" + e.currentTarget.dataset.id
    })
  },
  tapBanner: function(e) {
    const item = e.currentTarget.dataset.item
    if (item && item.link_type === 'food' && item.businessId) {
      wx.navigateTo({
        url: "/pages/goods-details/index?id=" + item.businessId
      })
    }
  },
  goDinnerPlan: function() {
    wx.switchTab({
      url: "/pages/shop-cart/index"
    })
  },
  onShareAppMessage: function() {
    return {
      title: '一起吃饭叭',
      path: '/pages/index/index'
    }
  }
})
