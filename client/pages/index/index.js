const WXAPI = require('../../wxapi/main')
const { normalizeImageUrl } = require('../../utils/api-adapter.js')

Page({
  data: {
    swiperCurrent: 0,
    bannerList: [],
    goodsRecommend: [],
    recentFoods: [],
    sharedPlan: null,
    recommendationText: '',
    recommendationLoading: false,
    recommendationItems: [],
    recommendationMessage: ''
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
    WXAPI.dinnerPlanCurrent().then(res => {
      if (res.code === 0) {
        this.setData({ sharedPlan: res.data && res.data.id ? res.data : null })
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
  goSharedPlan: function() {
    wx.navigateTo({ url: '/pages/dinner-plan/index' })
  },
  onRecommendationInput: function(e) {
    this.setData({ recommendationText: e.detail.value })
  },
  fillRecommendationExample: function(e) {
    this.setData({ recommendationText: e.currentTarget.dataset.text })
  },
  askRecommendation: function() {
    const text = (this.data.recommendationText || '').trim()
    if (text.length < 2) {
      wx.showToast({ title: '说说你想吃什么', icon: 'none' })
      return
    }
    if (this.data.recommendationLoading) return
    this.setData({ recommendationLoading: true, recommendationItems: [], recommendationMessage: '' })
    return WXAPI.recommendFoods({ text }).then(res => {
      if (res.code !== 0) return
      const data = res.data || {}
      this.setData({
        recommendationItems: (data.items || []).map(item => Object.assign({}, item, {
          image_url: normalizeImageUrl(item.image_url)
        })),
        recommendationMessage: data.message || ''
      })
    }).catch(() => {
      wx.showToast({ title: '推荐暂时不可用，请稍后再试', icon: 'none' })
    }).finally(() => this.setData({ recommendationLoading: false }))
  },
  onShareAppMessage: function() {
    return {
      title: '一起吃饭叭',
      path: '/pages/index/index'
    }
  }
})
