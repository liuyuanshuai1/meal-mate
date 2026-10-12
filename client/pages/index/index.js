const WXAPI = require('../../wxapi/main')
const { normalizeImageUrl } = require('../../utils/api-adapter.js')

Page({
  data: {
    bannerList: [],
    sharedPlan: null,
    recommendationText: '',
    recommendationMode: 'menu',
    recommendationLoading: false,
    recommendationItems: [],
    recommendationMessage: '',
    explorationItems: [],
    expandedExplorationIndex: -1
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
      if (res.code === 0) this.setData({ bannerList: res.data || [] })
    })
    WXAPI.dinnerPlanCurrent().then(res => {
      if (res.code === 0) {
        this.setData({ sharedPlan: res.data && res.data.id ? res.data : null })
      }
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
      wx.navigateTo({ url: '/pages/goods-details/index?id=' + item.businessId })
    }
  },
  goSharedPlan: function() {
    wx.navigateTo({ url: '/pages/dinner-plan/index' })
  },
  onRecommendationInput: function(e) {
    this.setData({ recommendationText: e.detail.value })
  },
  switchRecommendationMode: function(e) {
    const mode = e.currentTarget.dataset.mode
    if ((mode !== 'menu' && mode !== 'explore') || this.data.recommendationLoading) return
    this.setData({
      recommendationMode: mode,
      recommendationItems: [],
      explorationItems: [],
      expandedExplorationIndex: -1,
      recommendationMessage: ''
    })
  },
  toggleExplorationItem: function(e) {
    const index = Number(e.currentTarget.dataset.index)
    if (!Number.isInteger(index) || index < 0 || index >= this.data.explorationItems.length) return
    this.setData({ expandedExplorationIndex: this.data.expandedExplorationIndex === index ? -1 : index })
  },
  askRecommendation: function() {
    const text = (this.data.recommendationText || '').trim()
    if (text.length < 2) {
      wx.showToast({ title: '说说你想吃什么', icon: 'none' })
      return
    }
    if (this.data.recommendationLoading) return
    const explore = this.data.recommendationMode === 'explore'
    const request = explore ? WXAPI.exploreRecipes : WXAPI.recommendFoods
    this.setData({
      recommendationLoading: true,
      recommendationItems: [],
      explorationItems: [],
      expandedExplorationIndex: -1,
      recommendationMessage: ''
    })
    return request({ text }).then(res => {
      if (res.code !== 0) return
      const data = res.data || {}
      if (explore) {
        this.setData({
          explorationItems: (data.items || []).map(item => Object.assign({}, item, {
            missing_text: (item.missing_ingredients || []).join('、')
          })),
          recommendationMessage: data.message || ''
        })
      } else {
        this.setData({
          recommendationItems: (data.items || []).map(item => Object.assign({}, item, {
            image_url: normalizeImageUrl(item.image_url)
          })),
          recommendationMessage: data.message || ''
        })
      }
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
