const WXAPI = require('../../wxapi/main')
const WxParse = require('../../wxParse/wxParse.js')
const { mergeShopCarItem } = require('../../utils/dinner-plan.js')

Page({
  data: {
    goodsDetail: {
      basicInfo: {},
      pics: [],
      properties: []
    },
    shopNum: 0,
    buyNumber: 1,
    buyNumMin: 1,
    buyNumMax: 999,
    propertyChildIds: "",
    propertyChildNames: "",
    canSubmit: true,
    addingToCart: false,
    shopCarInfo: {},
    currentPages: undefined
  },
  onLoad(e) {
    this.data.goodsId = e.id
    const shopCarInfo = wx.getStorageSync('shopCarInfo') || {}
    this.setData({
      shopCarInfo,
      shopNum: shopCarInfo.shopNum || 0,
      currentPages: getCurrentPages()
    })
    this.loadGoodsDetail(e.id)
  },
  loadGoodsDetail(goodsId) {
    WXAPI.foodDetail(goodsId).then(res => {
      if (res.code !== 0) {
        return
      }
      const detail = res.data
      this.setData({
        goodsDetail: detail,
        buyNumMax: detail.basicInfo.stores || 999,
        buyNumber: 1,
        canSubmit: !(detail.properties && detail.properties.length)
      })
      WxParse.wxParse('article', 'html', detail.content || '', this, 5)
    })
  },
  goShopCar: function() {
    wx.switchTab({
      url: "/pages/shop-cart/index"
    })
  },
  numJianTap: function() {
    if (this.data.buyNumber > this.data.buyNumMin) {
      this.setData({
        buyNumber: this.data.buyNumber - 1
      })
    }
  },
  numJiaTap: function() {
    if (this.data.buyNumber < this.data.buyNumMax) {
      this.setData({
        buyNumber: this.data.buyNumber + 1
      })
    }
  },
  labelItemTap: function(e) {
    const goodsDetail = this.data.goodsDetail
    const property = goodsDetail.properties[e.currentTarget.dataset.propertyindex]
    property.childsCurGoods.forEach(child => {
      child.active = false
    })
    property.childsCurGoods[e.currentTarget.dataset.propertychildindex].active = true
    let curSelectNum = 0
    let propertyChildIds = ""
    let propertyChildNames = ""
    goodsDetail.properties.forEach(parent => {
      parent.childsCurGoods.forEach(child => {
        if (child.active) {
          curSelectNum++
          propertyChildIds += parent.id + ":" + child.id + ","
          propertyChildNames += parent.name + ":" + child.name + "  "
        }
      })
    })
    this.setData({
      goodsDetail,
      canSubmit: curSelectNum === goodsDetail.properties.length,
      propertyChildIds,
      propertyChildNames
    })
  },
  addShopCar: function() {
    if (this._addingToCart) {
      return
    }
    if (this.data.goodsDetail.properties && this.data.goodsDetail.properties.length && !this.data.canSubmit) {
      wx.showModal({
        content: '请选择口味或规格',
        showCancel: false
      })
      return
    }
    if (this.data.buyNumber < 1) {
      wx.showModal({
        title: '提示',
        content: '份数不能为0',
        showCancel: false
      })
      return
    }
    const basicInfo = this.data.goodsDetail.basicInfo
    const item = {
      goodsId: basicInfo.id,
      pic: basicInfo.pic,
      name: basicInfo.name,
      propertyChildIds: this.data.propertyChildIds,
      label: this.data.propertyChildNames,
      feeding_value: Number(basicInfo.feeding_value || 0),
      left: "",
      active: true,
      number: this.data.buyNumber
    }
    this._addingToCart = true
    this.setData({ addingToCart: true })
    let shopCarInfo
    try {
      shopCarInfo = mergeShopCarItem(wx.getStorageSync('shopCarInfo') || {}, item)
      wx.setStorageSync('shopCarInfo', shopCarInfo)
    } catch (error) {
      this._addingToCart = false
      this.setData({ addingToCart: false })
      wx.showToast({ title: '加入失败，请重试', icon: 'none' })
      return
    }
    this.setData({ shopCarInfo, shopNum: shopCarInfo.shopNum })
    wx.showToast({
      title: '已加入今晚菜单',
      icon: 'success'
    })
    const pages = getCurrentPages()
    if (pages.length > 1) {
      setTimeout(() => wx.navigateBack({ delta: 1, complete: () => {
        this._addingToCart = false
        this.setData({ addingToCart: false })
      } }), 350)
    } else {
      wx.switchTab({ url: '/pages/category/category', complete: () => {
        this._addingToCart = false
        this.setData({ addingToCart: false })
      } })
    }
  },
  onShareAppMessage: function() {
    return {
      title: this.data.goodsDetail.basicInfo.name,
      path: '/pages/goods-details/index?id=' + this.data.goodsDetail.basicInfo.id
    }
  },
  goIndex() {
    wx.switchTab({
      url: '/pages/index/index'
    })
  }
})
