const WXAPI = require('../../wxapi/main')
const {
  allSelect,
  buildDinnerPlanPayload,
  buildShopCarInfo,
  noSelect
} = require('../../utils/dinner-plan.js')

function dateText(date) {
  const pad = value => String(value).padStart(2, '0')
  return date.getFullYear() + '-' + pad(date.getMonth() + 1) + '-' + pad(date.getDate())
}

Page({
  data: {
    goodsList: {
      saveHidden: true,
      allSelect: true,
      noSelect: false,
      list: []
    },
    delBtnWidth: 120,
    submitting: false,
    reservationEnabled: false,
    reservationDate: '',
    reservationTime: '18:00',
    minDate: '',
    maxDate: '',
    members: [],
    feedingTotal: 0,
    unassignedCount: 0
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
    const today = new Date()
    const tomorrow = new Date(today.getTime())
    tomorrow.setDate(tomorrow.getDate() + 1)
    const latest = new Date(today.getTime())
    latest.setDate(latest.getDate() + 30)
    this.setData({ minDate: dateText(today), maxDate: dateText(latest), reservationDate: dateText(tomorrow) })
  },
  onShow: function() {
    const shopCarInfo = wx.getStorageSync('shopCarInfo') || {}
    this.setGoodsList(this.data.goodsList.saveHidden, shopCarInfo.shopList || [])
    WXAPI.diningGroupCurrent().then(res => {
      if (res.code !== 0 || !res.data || !res.data.id) {
        this.setData({ members: [] })
        return
      }
      const members = res.data.members || []
      this.setData({ members })
      const list = this.data.goodsList.list.map(item => Object.assign({}, item, { cook_options: members }))
      this.setGoodsList(this.data.goodsList.saveHidden, list)
    }).catch(() => this.setData({ members: [] }))
  },
  toIndexPage: function() {
    wx.switchTab({
      url: "/pages/category/category"
    })
  },
  viewRecipe: function(e) {
    const foodId = Number(e.currentTarget.dataset.id)
    if (!foodId) return
    wx.navigateTo({ url: '/pages/goods-details/index?id=' + foodId })
  },
  touchS: function(e) {
    if (e.touches.length == 1) {
      this.touchStartX = e.touches[0].clientX
      this.touchStartY = e.touches[0].clientY
      this.swipeDirection = null
    }
  },
  touchM: function(e) {
    const index = e.currentTarget.dataset.index
    if (e.touches.length == 1) {
      const moveX = e.touches[0].clientX
      const disX = this.touchStartX - moveX
      const disY = this.touchStartY - e.touches[0].clientY
      if (!this.swipeDirection && Math.max(Math.abs(disX), Math.abs(disY)) >= 8) {
        this.swipeDirection = Math.abs(disX) > Math.abs(disY) ? 'horizontal' : 'vertical'
      }
      if (this.swipeDirection !== 'horizontal') return
      const delBtnWidth = this.data.delBtnWidth
      let left = ""
      if (disX <= 0) {
        left = "margin-left:0px"
      } else {
        left = "margin-left:-" + Math.min(disX, delBtnWidth) + "px"
      }
      if (index !== "" && index != null) {
        this.setData({ ['goodsList.list[' + parseInt(index) + '].left']: left })
      }
    }
  },
  touchE: function(e) {
    if (this.swipeDirection !== 'horizontal') return
    const index = e.currentTarget.dataset.index
    if (e.changedTouches.length == 1) {
      const endX = e.changedTouches[0].clientX
      const disX = this.touchStartX - endX
      const delBtnWidth = this.data.delBtnWidth
      const left = disX > delBtnWidth / 2 ? "margin-left:-" + delBtnWidth + "px" : "margin-left:0px"
      if (index !== "" && index != null) {
        this.setData({ ['goodsList.list[' + parseInt(index) + '].left']: left })
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
    const nextList = (list || []).map((item, index) => Object.assign({}, item, {
      cartKey: item.goodsId == null ? 'row:' + index : String(item.goodsId) + ':' + (item.propertyChildIds || ''),
      feeding_value: Number(item.feeding_value || 0),
      total_feeding_value: Number(item.feeding_value || 0) * Number(item.number || 0)
    }))
    this.setData({
      goodsList: {
        saveHidden,
        allSelect: allSelect(nextList),
        noSelect: noSelect(nextList),
        list: nextList
      }
    })
    const selectedList = nextList.filter(item => item.active)
    this.setData({
      feedingTotal: selectedList.reduce((sum, item) => sum + Number(item.feeding_value || 0) * Number(item.number || 0), 0),
      unassignedCount: selectedList.filter(item => !item.cook_user_id).length
    })
    wx.setStorage({
      key: "shopCarInfo",
      data: buildShopCarInfo(nextList)
    })
  },
  selectCook: function(e) {
    const list = this.data.goodsList.list
    const index = Number(e.currentTarget.dataset.index)
    list[index].cook_user_id = Number(e.currentTarget.dataset.userId)
    this.setGoodsList(this.data.goodsList.saveHidden, list)
  },
  toggleReservation: function(e) {
    this.setData({ reservationEnabled: !!e.detail.value })
  },
  changeReservationDate: function(e) {
    this.setData({ reservationDate: e.detail.value })
  },
  changeReservationTime: function(e) {
    this.setData({ reservationTime: e.detail.value })
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
    if (this.data.members.length < 2) {
      wx.showToast({ title: '先创建饭搭子并邀请对方加入', icon: 'none' })
      wx.navigateTo({ url: '/pages/partner/index' })
      return
    }
    const unassigned = selected.find(item => !item.cook_user_id)
    if (unassigned) {
      wx.showToast({ title: '请先给「' + unassigned.name + '」选择做菜人', icon: 'none' })
      return
    }
    if (this.data.submitting) {
      return
    }
    const payload = buildDinnerPlanPayload(list)
    if (this.data.reservationEnabled) {
      const scheduled = new Date(this.data.reservationDate + 'T' + this.data.reservationTime + ':00')
      const minutesUntil = (scheduled.getTime() - Date.now()) / 60000
      if (!Number.isFinite(minutesUntil) || minutesUntil < 10 || minutesUntil > 30 * 24 * 60) {
        wx.showToast({ title: '请选择 10 分钟后、30 天内的时间', icon: 'none' })
        return
      }
      payload.scheduled_for = scheduled.toISOString()
    }
    this.setData({ submitting: true })
    wx.showLoading({ title: '发送中' })
    return WXAPI.diningGroupCurrent().then(groupRes => {
      if (groupRes.code !== 0) {
        return groupRes
      }
      if (!groupRes.data || !groupRes.data.id || groupRes.data.members.length < 2) {
        wx.hideLoading()
        this.setData({ submitting: false })
        wx.showToast({ title: '等饭搭子加入后再发送', icon: 'none' })
        wx.navigateTo({ url: '/pages/partner/index' })
        return null
      }
      return WXAPI.createDinnerPlan(payload)
    }).then(res => {
      if (!res) {
        return
      }
      wx.hideLoading()
      this.setData({ submitting: false })
      if (res.code === 0) {
        wx.removeStorageSync("shopCarInfo")
        this.setData({
          goodsList: {
            saveHidden: true,
            allSelect: false,
            noSelect: true,
            list: []
          }
        })
        wx.showToast({
          title: this.data.reservationEnabled ? '预约已发给饭搭子' : '已发给饭搭子',
          icon: 'success'
        })
        wx.navigateTo({
          url: "/pages/dinner-plan/index?id=" + res.data.id
        })
        return
      }
      wx.showToast({
        title: res.message || '发送失败，请稍后再试',
        icon: 'none'
      })
    }).catch(() => {
      wx.hideLoading()
      this.setData({ submitting: false })
      wx.showToast({
        title: '发送失败，请稍后再试',
        icon: 'none'
      })
    })
  }
})
