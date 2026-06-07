const WXAPI = require('../../wxapi/main')
const CONFIG = require('../../config.js')
const {
  allSelect,
  buildEatRecordPayload,
  buildShopCarInfo,
  noSelect,
  totalPrice
} = require('../../utils/dinner-plan.js')

Page({
  data: {
    goodsList: {
      saveHidden: true,
      totalPrice: 0,
      allSelect: true,
      noSelect: false,
      list: []
    },
    delBtnWidth: 120,
    submitting: false
  },
  getEleWidth: function(w) {
    try {
      const res = wx.getWindowInfo ? wx.getWindowInfo().windowWidth : wx.getSystemInfoSync().windowWidth
      const scale = (750 / 2) / (w / 2)
      return Math.floor(res / scale)
    } catch (e) {
      return false
    }
  },
  initEleWidth: function() {
    this.setData({
      delBtnWidth: this.getEleWidth(this.data.delBtnWidth)
    })
  },
  onLoad: function() {
    this.initEleWidth()
  },
  onShow: function() {
    const shopCarInfo = wx.getStorageSync('shopCarInfo') || {}
    this.setGoodsList(this.data.goodsList.saveHidden, shopCarInfo.shopList || [])
  },
  toIndexPage: function() {
    wx.switchTab({
      url: "/pages/category/category"
    })
  },
  touchS: function(e) {
    if (e.touches.length == 1) {
      this.setData({
        startX: e.touches[0].clientX
      })
    }
  },
  touchM: function(e) {
    const index = e.currentTarget.dataset.index
    if (e.touches.length == 1) {
      const moveX = e.touches[0].clientX
      const disX = this.data.startX - moveX
      const delBtnWidth = this.data.delBtnWidth
      let left = ""
      if (disX <= 0) {
        left = "margin-left:0px"
      } else {
        left = "margin-left:-" + Math.min(disX, delBtnWidth) + "px"
      }
      const list = this.data.goodsList.list
      if (index !== "" && index != null) {
        list[parseInt(index)].left = left
        this.setGoodsList(this.data.goodsList.saveHidden, list)
      }
    }
  },
  touchE: function(e) {
    const index = e.currentTarget.dataset.index
    if (e.changedTouches.length == 1) {
      const endX = e.changedTouches[0].clientX
      const disX = this.data.startX - endX
      const delBtnWidth = this.data.delBtnWidth
      const left = disX > delBtnWidth / 2 ? "margin-left:-" + delBtnWidth + "px" : "margin-left:0px"
      const list = this.data.goodsList.list
      if (index !== "" && index != null) {
        list[parseInt(index)].left = left
        this.setGoodsList(this.data.goodsList.saveHidden, list)
      }
    }
  },
  delItem: function(e) {
    const list = this.data.goodsList.list
    list.splice(e.currentTarget.dataset.index, 1)
    this.setGoodsList(this.data.goodsList.saveHidden, list)
  },
  selectTap: function(e) {
    const index = e.currentTarget.dataset.index
    const list = this.data.goodsList.list
    if (index !== "" && index != null) {
      list[parseInt(index)].active = !list[parseInt(index)].active
      this.setGoodsList(this.data.goodsList.saveHidden, list)
    }
  },
  setGoodsList: function(saveHidden, list) {
    const nextList = list || []
    this.setData({
      goodsList: {
        saveHidden,
        totalPrice: totalPrice(nextList),
        allSelect: allSelect(nextList),
        noSelect: noSelect(nextList),
        list: nextList
      }
    })
    wx.setStorage({
      key: "shopCarInfo",
      data: buildShopCarInfo(nextList)
    })
  },
  bindAllSelect: function() {
    const currentAllSelect = this.data.goodsList.allSelect
    const list = this.data.goodsList.list
    list.forEach(item => {
      item.active = !currentAllSelect
    })
    this.setGoodsList(this.data.goodsList.saveHidden, list)
  },
  jiaBtnTap: function(e) {
    const index = e.currentTarget.dataset.index
    const list = this.data.goodsList.list
    if (index !== "" && index != null) {
      list[parseInt(index)].number++
      this.setGoodsList(this.data.goodsList.saveHidden, list)
    }
  },
  jianBtnTap: function(e) {
    const index = e.currentTarget.dataset.index
    const list = this.data.goodsList.list
    if (index !== "" && index != null && list[parseInt(index)].number > 1) {
      list[parseInt(index)].number--
      this.setGoodsList(this.data.goodsList.saveHidden, list)
    }
  },
  editTap: function() {
    const list = this.data.goodsList.list
    list.forEach(item => {
      item.active = false
    })
    this.setGoodsList(false, list)
  },
  saveTap: function() {
    const list = this.data.goodsList.list
    list.forEach(item => {
      item.active = true
    })
    this.setGoodsList(true, list)
  },
  deleteSelected: function() {
    const list = this.data.goodsList.list.filter(item => !item.active)
    this.setGoodsList(this.data.goodsList.saveHidden, list)
  },
  toPayOrder: function() {
    const list = this.data.goodsList.list
    const selected = list.filter(item => item.active)
    if (!selected.length) {
      wx.showToast({
        title: '还没选好今晚吃什么',
        icon: 'none'
      })
      return
    }
    if (this.data.submitting) {
      return
    }
    this.setData({ submitting: true })
    wx.showLoading({ title: '记录中' })
    WXAPI.createEatRecord(buildEatRecordPayload(list, CONFIG, '')).then(res => {
      wx.hideLoading()
      this.setData({ submitting: false })
      if (res.code === 0) {
        wx.removeStorageSync("shopCarInfo")
        this.setData({
          goodsList: {
            saveHidden: true,
            totalPrice: 0,
            allSelect: false,
            noSelect: true,
            list: []
          }
        })
        wx.showToast({
          title: '已记录这顿饭',
          icon: 'success'
        })
        wx.navigateTo({
          url: "/pages/eat-records/index"
        })
        return
      }
      wx.showToast({
        title: res.message || '记录失败，请稍后再试',
        icon: 'none'
      })
    }).catch(() => {
      wx.hideLoading()
      this.setData({ submitting: false })
      wx.showToast({
        title: '记录失败，请稍后再试',
        icon: 'none'
      })
    })
  }
})
